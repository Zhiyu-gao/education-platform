package com.ruoyi.student.controller;

import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.constant.Constants;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.utils.DateUtils;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.framework.security.context.AuthenticationContextHolder;
import com.ruoyi.framework.web.service.SysLoginService;
import com.ruoyi.framework.web.service.TokenService;
import com.ruoyi.student.domain.EduLoginBody;
import com.ruoyi.student.domain.EduRegisterBody;
import com.ruoyi.student.mapper.EduPadMapper;
import com.ruoyi.system.mapper.SysRoleMapper;
import com.ruoyi.system.service.ISysUserService;

/**
 * Pad 端认证接口（匿名）
 */
@RestController
public class EduAuthController extends BaseController
{
    private static final String ROLE_TEACHER = "teacher";
    private static final String ROLE_STUDENT = "student";

    @Autowired
    private ISysUserService userService;

    @Autowired
    private SysRoleMapper roleMapper;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private TokenService tokenService;

    @Autowired
    private SysLoginService loginService;

    @Autowired
    private EduPadMapper eduPadMapper;

    @PostMapping("/student/performance/anonymous/education/login")
    public AjaxResult login(@RequestBody EduLoginBody loginBody)
    {
        String username = StringUtils.trim(loginBody.getUsername());
        String password = loginBody.getPassword();
        Integer gradeNo = loginBody.getGradeNo();
        Integer classNo = loginBody.getClassNo();

        if (!isValidGradeClass(gradeNo, classNo))
        {
            return error("请选择正确的年级和班级（年级1-5，班级1-10）");
        }

        loginService.loginPreCheck(username, password);

        Authentication authentication;
        try
        {
            UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(username, password);
            AuthenticationContextHolder.setContext(authenticationToken);
            authentication = authenticationManager.authenticate(authenticationToken);
        }
        catch (Exception e)
        {
            if (e instanceof BadCredentialsException)
            {
                return error("用户名或密码错误");
            }
            return error(StringUtils.isEmpty(e.getMessage()) ? "登录失败" : e.getMessage());
        }
        finally
        {
            AuthenticationContextHolder.clearContext();
        }

        LoginUser loginUser = (LoginUser) authentication.getPrincipal();
        if (!validateClassOnLogin(loginUser.getUserId(), gradeNo, classNo))
        {
            return error("所选年级班级与账号不匹配，请确认后重试");
        }
        loginService.recordLoginInfo(loginUser.getUserId());

        AjaxResult ajax = AjaxResult.success();
        ajax.put(Constants.TOKEN, tokenService.createToken(loginUser));
        return ajax;
    }

    @PostMapping("/student/performance/anonymous/education/register")
    public AjaxResult register(@RequestBody EduRegisterBody registerBody)
    {
        String msg = registerInternal(registerBody);
        return StringUtils.isEmpty(msg) ? success() : error(msg);
    }

    private String registerInternal(EduRegisterBody registerBody)
    {
        String username = registerBody.getUsername();
        String password = registerBody.getPassword();
        String roleKey = normalizeRoleKey(registerBody.getRoleKey());
        Integer gradeNo = registerBody.getGradeNo();
        Integer classNo = registerBody.getClassNo();
        SysUser sysUser = new SysUser();
        sysUser.setUserName(username);

        if (StringUtils.isEmpty(username))
        {
            return "用户名不能为空";
        }
        if (StringUtils.isEmpty(password))
        {
            return "用户密码不能为空";
        }
        if (StringUtils.isEmpty(roleKey))
        {
            return "注册角色无效，仅支持 teacher 或 student";
        }
        if (!isValidGradeClass(gradeNo, classNo))
        {
            return "请选择正确的年级和班级（年级1-5，班级1-10）";
        }
        if (username.length() < UserConstants.USERNAME_MIN_LENGTH || username.length() > UserConstants.USERNAME_MAX_LENGTH)
        {
            return "账户长度必须在2到20个字符之间";
        }
        if (password.length() < UserConstants.PASSWORD_MIN_LENGTH || password.length() > UserConstants.PASSWORD_MAX_LENGTH)
        {
            return "密码长度必须在5到20个字符之间";
        }
        if (!userService.checkUserNameUnique(sysUser))
        {
            return "保存用户'" + username + "'失败，注册账号已存在";
        }

        SysRole role = roleMapper.checkRoleKeyUnique(roleKey);
        if (role == null)
        {
            return "注册失败，系统未配置角色：" + roleKey;
        }
        if (!"0".equals(role.getStatus()))
        {
            return "注册失败，角色已停用：" + roleKey;
        }

        sysUser.setNickName(username);
        sysUser.setPwdUpdateDate(DateUtils.getNowDate());
        sysUser.setPassword(SecurityUtils.encryptPassword(password));
        sysUser.setRoleIds(new Long[] { role.getRoleId() });

        boolean success = userService.registerUser(sysUser);
        if (!success)
        {
            return "注册失败,请联系系统管理人员";
        }

        SysUser created = userService.selectUserByUserName(username);
        if (created == null || created.getUserId() == null)
        {
            return "注册失败，无法获取用户信息";
        }
        String className = buildClassName(gradeNo, classNo);
        int rows = eduPadMapper.upsertUserClassProfile(
                created.getUserId(),
                roleKey,
                gradeNo,
                classNo,
                className,
                ROLE_TEACHER.equals(roleKey) ? 1 : 0);
        if (rows <= 0)
        {
            return "注册失败，班级信息写入失败";
        }
        return "";
    }

    private String normalizeRoleKey(String roleKey)
    {
        String normalized = StringUtils.trimToEmpty(roleKey).toLowerCase();
        if (ROLE_TEACHER.equals(normalized))
        {
            return ROLE_TEACHER;
        }
        if (ROLE_STUDENT.equals(normalized))
        {
            return ROLE_STUDENT;
        }
        return "";
    }

    private boolean isValidGradeClass(Integer gradeNo, Integer classNo)
    {
        if (gradeNo == null || classNo == null)
        {
            return false;
        }
        return gradeNo >= 1 && gradeNo <= 5 && classNo >= 1 && classNo <= 10;
    }

    private String buildClassName(Integer gradeNo, Integer classNo)
    {
        return "G" + gradeNo + "-C" + classNo;
    }

    private boolean validateClassOnLogin(Long userId, Integer gradeNo, Integer classNo)
    {
        Map<String, Object> profile = eduPadMapper.selectUserClassProfileByUserId(userId);
        if (profile == null || profile.isEmpty()) {
            String roleKey = resolveRoleKey(userId);
            if (StringUtils.isEmpty(roleKey)) {
                return false;
            }
            int rows = eduPadMapper.upsertUserClassProfile(
                    userId,
                    roleKey,
                    gradeNo,
                    classNo,
                    buildClassName(gradeNo, classNo),
                    ROLE_TEACHER.equals(roleKey) ? 1 : 0
            );
            return rows > 0;
        }
        Object pGrade = profile.get("grade_no");
        Object pClass = profile.get("class_no");
        if (!(pGrade instanceof Number) || !(pClass instanceof Number))
        {
            return false;
        }
        return ((Number) pGrade).intValue() == gradeNo.intValue()
                && ((Number) pClass).intValue() == classNo.intValue();
    }

    private String resolveRoleKey(Long userId)
    {
        for (SysRole role : roleMapper.selectRolePermissionByUserId(userId))
        {
            if (ROLE_TEACHER.equalsIgnoreCase(role.getRoleKey()))
            {
                return ROLE_TEACHER;
            }
            if (ROLE_STUDENT.equalsIgnoreCase(role.getRoleKey()) || "role_default".equalsIgnoreCase(role.getRoleKey()))
            {
                return ROLE_STUDENT;
            }
        }
        return "";
    }
}
