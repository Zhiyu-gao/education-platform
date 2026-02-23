package com.ruoyi.student.controller;

import java.util.Date;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.constant.Constants;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.common.utils.DateUtils;
import com.ruoyi.framework.security.context.AuthenticationContextHolder;
import com.ruoyi.framework.web.service.SysLoginService;
import com.ruoyi.framework.web.service.TokenService;
import com.ruoyi.student.domain.EduExam;
import com.ruoyi.student.domain.EduExamScore;
import com.ruoyi.student.domain.EduForumPost;
import com.ruoyi.student.domain.EduForumReply;
import com.ruoyi.student.domain.EduHomework;
import com.ruoyi.student.domain.EduHomeworkSubmission;
import com.ruoyi.student.domain.EduLoginBody;
import com.ruoyi.student.domain.EduRegisterBody;
import com.ruoyi.student.domain.EduTeacherTask;
import com.ruoyi.student.mapper.EduPadMapper;
import com.ruoyi.system.mapper.SysRoleMapper;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.system.service.ISysUserService;

@RestController
@RequestMapping("/education/pad")
public class EduPadController extends BaseController {
    private static final Logger log = LoggerFactory.getLogger(EduPadController.class);
    private static final int MIN_GRADE_NO = 1;
    private static final int MAX_GRADE_NO = 5;
    private static final int MIN_CLASS_NO = 1;
    private static final int MAX_CLASS_NO = 10;
    private static final int HOMEWORK_MIN_SCORE = 0;
    private static final int HOMEWORK_MAX_SCORE = 100;
    private static final int DEFAULT_EXAM_MAX_SCORE = 100;
    private static final int DEFAULT_EXAMPLE_SCORE = 80;
    private static final int MIN_AI_FALLBACK_SCORE = 60;
    private static final String STATUS_PUBLISHED = "PUBLISHED";
    private static final String STATUS_TODO = "TODO";
    private static final String CHAT_DM_TITLE = "CHAT_DM";
    private static final String CHAT_GROUP_TITLE = "CHAT_GROUP";
    private static final String DEFAULT_CLASS_GROUP_ID = "CLASS_ALL";
    private static final String ROLE_KEY_TEACHER = "teacher";
    private static final String ROLE_KEY_STUDENT = "student";
    private static final String ROLE_KEY_DEFAULT_STUDENT = "role_default";
    private static final String CLASS_NAME_KEY = "class_name";
    private static final String GRADE_NO_KEY = "grade_no";
    private static final String CLASS_NO_KEY = "class_no";
    private static final String ROLE_KEY_KEY = "role_key";
    private static final String POST_ID_KEY = "post_id";
    private static final String ROLE_MANAGER = "MANAGER";
    private static final String ROLE_TEACHER = "TEACHER";
    private static final String ROLE_STUDENT = "STUDENT";
    private static final String ROLE_ALL = "ALL";

    @Autowired
    private EduPadMapper eduPadMapper;

    @Autowired
    private SysRoleMapper roleMapper;

    @Autowired
    private ISysUserService userService;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private TokenService tokenService;

    @Autowired
    private SysLoginService loginService;

    @PostMapping("/auth/login")
    public AjaxResult padAuthLogin(@RequestBody EduLoginBody loginBody) {
        String username = StringUtils.trim(loginBody.getUsername());
        String password = loginBody.getPassword();
        Integer gradeNo = loginBody.getGradeNo();
        Integer classNo = loginBody.getClassNo();
        if (!isValidGradeClass(gradeNo, classNo)) {
            return error("请选择正确的年级和班级（年级1-5，班级1-10）");
        }

        loginService.loginPreCheck(username, password);
        Authentication authentication;
        try {
            UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(username, password);
            AuthenticationContextHolder.setContext(authenticationToken);
            authentication = authenticationManager.authenticate(authenticationToken);
        } catch (Exception e) {
            if (e instanceof BadCredentialsException) {
                return error("用户名或密码错误");
            }
            return error(StringUtils.isEmpty(e.getMessage()) ? "登录失败" : e.getMessage());
        } finally {
            AuthenticationContextHolder.clearContext();
        }

        LoginUser loginUser = (LoginUser) authentication.getPrincipal();
        if (!validateClassOnLogin(loginUser.getUserId(), gradeNo, classNo)) {
            return error("所选年级班级与账号不匹配，请确认后重试");
        }
        loginService.recordLoginInfo(loginUser.getUserId());
        AjaxResult ajax = AjaxResult.success();
        ajax.put(Constants.TOKEN, tokenService.createToken(loginUser));
        return ajax;
    }

    @PostMapping("/auth/register")
    public AjaxResult padAuthRegister(@RequestBody EduRegisterBody registerBody) {
        String msg = registerPadUser(registerBody);
        return StringUtils.isEmpty(msg) ? success() : error(msg);
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/homework")
    public AjaxResult createHomework(@Validated @RequestBody EduHomework homework) {
        fillTeacherInfo(homework);
        if (isTeacherRole()) {
            String className = getCurrentClassName();
            if (StringUtils.isEmpty(className)) {
                return error("老师未绑定班级，请先在登录页选择班级后登录");
            }
            homework.setClassName(className);
        }
        if (homework.getStatus() == null) {
            homework.setStatus(STATUS_PUBLISHED);
        }
        return toAjax(eduPadMapper.insertHomework(homework));
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @GetMapping("/homework/teacher")
    public AjaxResult listTeacherHomework() {
        return success(eduPadMapper.selectHomeworkByTeacherId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @GetMapping("/homework/student")
    public AjaxResult listStudentHomework() {
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return emptyListSuccess();
        }
        return success(eduPadMapper.selectHomeworkByClassName(className));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @PostMapping("/homework/{homeworkId}/submit")
    public AjaxResult submitHomework(@PathVariable Long homeworkId, @RequestBody EduHomeworkSubmission submission) {
        Long studentId = SecurityUtils.getUserId();
        if (submission == null) {
            log.warn("学生提交作业参数为空: homeworkId={}, studentId={}", homeworkId, studentId);
            return error("提交参数不能为空");
        }
        String answerContent = submission.getAnswerContent();
        log.info("学生提交作业请求: homeworkId={}, studentId={}, answerLength={}, hasImageMarker={}",
                homeworkId,
                studentId,
                answerContent == null ? 0 : answerContent.length(),
                answerContent != null && answerContent.contains("![作答图片]("));
        Long exists = eduPadMapper.selectHomeworkSubmissionExists(homeworkId, studentId);
        if (exists != null) {
            log.warn("学生重复提交作业: homeworkId={}, studentId={}, submissionId={}", homeworkId, studentId, exists);
            return error("该作业已提交，无需重复提交");
        }
        submission.setHomeworkId(homeworkId);
        submission.setStudentId(studentId);
        submission.setStudentName(SecurityUtils.getLoginUser().getUser().getNickName());
        submission.setSubmitTime(new Date());
        int rows = eduPadMapper.insertHomeworkSubmission(submission);
        log.info("学生提交作业完成: homeworkId={}, studentId={}, rows={}", homeworkId, studentId, rows);
        return toAjax(rows);
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @GetMapping("/homework/submissions")
    public AjaxResult listHomeworkSubmissionsByTeacher() {
        return success(eduPadMapper.selectHomeworkSubmissionByTeacherId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @GetMapping("/homework/submissions/student")
    public AjaxResult listHomeworkSubmissionsByStudent() {
        return success(eduPadMapper.selectHomeworkSubmissionByStudentId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @PostMapping("/homework/score")
    public AjaxResult scoreHomework(@RequestBody EduHomeworkSubmission submission) {
        if (submission == null || submission.getSubmissionId() == null) {
            return error("提交记录ID不能为空");
        }
        if (submission.getScore() == null || submission.getScore() < HOMEWORK_MIN_SCORE || submission.getScore() > HOMEWORK_MAX_SCORE) {
            return error("作业分数必须在" + HOMEWORK_MIN_SCORE + "-" + HOMEWORK_MAX_SCORE + "之间");
        }
        Map<String, Object> current = eduPadMapper.selectHomeworkSubmissionById(submission.getSubmissionId());
        if (current == null || current.isEmpty()) {
            return error("提交记录不存在");
        }
        Object teacherIdObj = current.get("teacher_id");
        if (!(teacherIdObj instanceof Number) || ((Number) teacherIdObj).longValue() != currentUserId()) {
            return error("只能批改自己发布作业的提交");
        }
        int rows = eduPadMapper.updateHomeworkSubmissionScore(submission);
        if (rows > 0) {
            notifyHomeworkReviewed(current, submission);
        }
        return toAjax(rows);
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/exam")
    public AjaxResult createExam(@Validated @RequestBody EduExam exam) {
        exam.setTeacherId(currentUserId());
        exam.setTeacherName(currentUserNickName());
        if (isTeacherRole()) {
            String className = getCurrentClassName();
            if (StringUtils.isEmpty(className)) {
                return error("老师未绑定班级，请先在登录页选择班级后登录");
            }
            exam.setClassName(className);
        }
        return toAjax(eduPadMapper.insertExam(exam));
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @GetMapping("/exam/teacher")
    public AjaxResult listTeacherExam() {
        return success(eduPadMapper.selectExamByTeacherId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @GetMapping("/exam/student")
    public AjaxResult listStudentExam() {
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return emptyListSuccess();
        }
        return success(eduPadMapper.selectExamByClassName(className));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @PostMapping("/exam/{examId}/submit")
    public AjaxResult submitExam(@PathVariable Long examId, @RequestBody Map<String, Object> body) {
        EduExam exam = eduPadMapper.selectExamById(examId);
        if (exam == null) {
            return error("考试不存在");
        }
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className) || !className.equals(exam.getClassName())) {
            return error("只能提交自己班级的考试");
        }
        String answerContent = body == null ? "" : String.valueOf(body.getOrDefault("answerContent", "")).trim();
        if (StringUtils.isEmpty(answerContent)) {
            return error("请填写考试作答内容");
        }

        EduExamScore examScore = new EduExamScore();
        examScore.setExamId(examId);
        examScore.setStudentId(currentUserId());
        examScore.setStudentName(currentUserNickName());
        examScore.setScore(null);
        examScore.setRemark(answerContent);
        return toAjax(eduPadMapper.upsertExamScore(examScore));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/exam/score")
    public AjaxResult scoreExam(@Validated @RequestBody EduExamScore examScore) {
        if (isTeacherRole()) {
            String className = getCurrentClassName();
            if (StringUtils.isEmpty(className)) {
                return error("老师未绑定班级");
            }
            Integer matched = eduPadMapper.countStudentInClassByUserId(examScore.getStudentId(), className);
            if (matched == null || matched <= 0) {
                return error("只能为自己班级的学生评分");
            }
        }
        if (examScore.getStudentName() == null || examScore.getStudentName().isEmpty()) {
            examScore.setStudentName("student-" + examScore.getStudentId());
        }
        return toAjax(eduPadMapper.upsertExamScore(examScore));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @GetMapping("/exam/score/student")
    public AjaxResult listStudentExamScore() {
        return success(eduPadMapper.selectExamScoreByStudentId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @GetMapping("/exam/score/teacher")
    public AjaxResult listTeacherExamScore() {
        return success(eduPadMapper.selectExamScoreByTeacherId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('admin') or @ss.hasRole('manager')")
    @GetMapping("/manager/scores")
    public AjaxResult listManagerAllScores() {
        AjaxResult result = AjaxResult.success();
        result.put("examScores", eduPadMapper.selectExamScoreAll());
        result.put("performanceScores", eduPadMapper.selectStudentPerformanceAll());
        return result;
    }

    @PreAuthorize("@ss.hasRole('student')")
    @GetMapping("/student/scores")
    public AjaxResult listStudentSelfScores() {
        AjaxResult result = AjaxResult.success();
        result.put("examScores", eduPadMapper.selectExamScoreByStudentId(currentUserId()));
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            result.put("performanceScores", Collections.emptyList());
        } else {
            result.put("performanceScores", eduPadMapper.selectStudentPerformanceByClassName(className));
        }
        return result;
    }

    @PreAuthorize("@ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/manager/teacher-task")
    public AjaxResult createTeacherTask(@Validated @RequestBody EduTeacherTask task) {
        if (task.getStatus() == null) {
            task.setStatus(STATUS_TODO);
        }
        return toAjax(eduPadMapper.insertTeacherTask(task));
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @GetMapping("/teacher/tasks")
    public AjaxResult listTeacherTasks() {
        return success(eduPadMapper.selectTeacherTaskByTeacherId(SecurityUtils.getUserId()));
    }

    @PreAuthorize("@ss.hasRole('teacher')")
    @GetMapping("/teacher/scores")
    public AjaxResult listTeacherStudentScores() {
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return emptyListSuccess();
        }
        return success(eduPadMapper.selectStudentPerformanceByClassName(className));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('student')")
    @GetMapping("/chat/contacts")
    public AjaxResult listChatContacts() {
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return emptyListSuccess();
        }
        String currentRole = resolveCurrentForumRole();
        String peerRole = ROLE_TEACHER.equals(currentRole) ? ROLE_KEY_STUDENT : ROLE_KEY_TEACHER;
        return success(eduPadMapper.selectClassChatContacts(className, currentUserId(), peerRole));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('student')")
    @GetMapping("/chat/messages")
    public AjaxResult listChatMessages(Long peerUserId) {
        if (peerUserId == null || peerUserId <= 0) {
            return error("聊天对象不能为空");
        }
        if (!canChatWith(peerUserId)) {
            return error("只能与本班可联系对象聊天");
        }
        String className = getCurrentClassName();
        Long currentUserId = currentUserId();
        return success(eduPadMapper.selectChatMessages(
                className,
                currentUserId,
                peerUserId,
                String.valueOf(currentUserId),
                String.valueOf(peerUserId)));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('student')")
    @GetMapping("/chat/groups")
    public AjaxResult listChatGroups() {
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return emptyListSuccess();
        }
        List<Map<String, Object>> groups = new ArrayList<>();
        Map<String, Object> classGroup = new HashMap<>();
        classGroup.put("groupId", DEFAULT_CLASS_GROUP_ID);
        classGroup.put("groupName", className + " 群聊");
        classGroup.put("className", className);
        groups.add(classGroup);
        return success(groups);
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('student')")
    @GetMapping("/chat/group/messages")
    public AjaxResult listGroupChatMessages(String groupId) {
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return emptyListSuccess();
        }
        if (StringUtils.isEmpty(groupId) || !DEFAULT_CLASS_GROUP_ID.equals(groupId)) {
            return error("群聊不存在或无权限访问");
        }
        return success(eduPadMapper.selectGroupChatMessages(className, groupId));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('student')")
    @PostMapping("/chat/send")
    public AjaxResult sendChatMessage(@RequestBody Map<String, Object> body) {
        Long peerUserId = toLong(body == null ? null : body.get("peerUserId"));
        String content = body == null ? "" : String.valueOf(body.getOrDefault("content", "")).trim();
        if (peerUserId == null || peerUserId <= 0) {
            return error("聊天对象不能为空");
        }
        if (StringUtils.isEmpty(content)) {
            return error("消息内容不能为空");
        }
        if (!canChatWith(peerUserId)) {
            return error("只能与本班可联系对象聊天");
        }
        EduForumPost msg = new EduForumPost();
        msg.setTitle(CHAT_DM_TITLE);
        msg.setContent(content);
        msg.setAuthorId(currentUserId());
        msg.setAuthorName(currentUserNickName());
        msg.setAuthorRole(resolveCurrentForumRole());
        msg.setTargetRole(String.valueOf(peerUserId));
        msg.setClassName(getCurrentClassName());
        return toAjax(eduPadMapper.insertForumPost(msg));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('student')")
    @PostMapping("/chat/group/send")
    public AjaxResult sendGroupChatMessage(@RequestBody Map<String, Object> body) {
        String groupId = body == null ? "" : String.valueOf(body.getOrDefault("groupId", "")).trim();
        String content = body == null ? "" : String.valueOf(body.getOrDefault("content", "")).trim();
        if (StringUtils.isEmpty(groupId) || !DEFAULT_CLASS_GROUP_ID.equals(groupId)) {
            return error("群聊不存在或无权限发送");
        }
        if (StringUtils.isEmpty(content)) {
            return error("消息内容不能为空");
        }
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            return error("未绑定班级，无法发送群消息");
        }
        EduForumPost msg = new EduForumPost();
        msg.setTitle(CHAT_GROUP_TITLE);
        msg.setContent(content);
        msg.setAuthorId(currentUserId());
        msg.setAuthorName(currentUserNickName());
        msg.setAuthorRole(resolveCurrentForumRole());
        msg.setTargetRole(groupId);
        msg.setClassName(className);
        return toAjax(eduPadMapper.insertForumPost(msg));
    }

    @GetMapping("/forum/posts")
    public AjaxResult listForumPosts() {
        String role = resolveCurrentForumRole();
        String className = getCurrentClassName();
        List<Map<String, Object>> posts = ROLE_MANAGER.equals(role)
                ? eduPadMapper.selectForumPostsAll()
                : eduPadMapper.selectForumPostsByRole(role, className);

        if (posts == null || posts.isEmpty()) {
            return emptyListSuccess();
        }

        List<Long> postIds = posts.stream()
                .map(item -> Long.valueOf(String.valueOf(item.get(POST_ID_KEY))))
                .collect(Collectors.toList());
        List<Map<String, Object>> replies = eduPadMapper.selectForumRepliesByPostIds(postIds);
        Map<Long, List<Map<String, Object>>> replyMap = new HashMap<>();
        if (replies != null) {
            for (Map<String, Object> reply : replies) {
                Long postId = Long.valueOf(String.valueOf(reply.get(POST_ID_KEY)));
                replyMap.computeIfAbsent(postId, key -> new ArrayList<>()).add(reply);
            }
        }

        for (Map<String, Object> post : posts) {
            Long postId = Long.valueOf(String.valueOf(post.get(POST_ID_KEY)));
            post.put("replies", replyMap.getOrDefault(postId, new ArrayList<>()));
        }

        return success(posts);
    }

    @PostMapping("/forum/post")
    public AjaxResult createForumPost(@RequestBody EduForumPost post) {
        if (post == null || post.getTitle() == null || post.getTitle().trim().isEmpty()) {
            return error("标题不能为空");
        }
        if (post.getContent() == null || post.getContent().trim().isEmpty()) {
            return error("内容不能为空");
        }

        String role = resolveCurrentForumRole();
        String targetRole = normalizeTargetRole(post.getTargetRole(), role);
        if (targetRole == null) {
            return error("目标角色无效");
        }

        post.setAuthorId(currentUserId());
        post.setAuthorName(currentUserNickName());
        post.setAuthorRole(role);
        post.setTargetRole(targetRole);
        if (!ROLE_MANAGER.equals(role)) {
            String className = getCurrentClassName();
            if (StringUtils.isEmpty(className)) {
                return error("未绑定班级，无法发送消息");
            }
            post.setClassName(className);
        }
        return toAjax(eduPadMapper.insertForumPost(post));
    }

    @PostMapping("/forum/{postId}/reply")
    public AjaxResult replyForumPost(@PathVariable Long postId, @RequestBody EduForumReply reply) {
        if (reply == null || reply.getContent() == null || reply.getContent().trim().isEmpty()) {
            return error("回复内容不能为空");
        }
        reply.setPostId(postId);
        reply.setAuthorId(currentUserId());
        reply.setAuthorName(currentUserNickName());
        reply.setAuthorRole(resolveCurrentForumRole());
        return toAjax(eduPadMapper.insertForumReply(reply));
    }

    @GetMapping("/forum/notice")
    public AjaxResult getForumNotice() {
        Long userId = SecurityUtils.getUserId();
        String role = resolveCurrentForumRole();
        Date readTime = eduPadMapper.selectForumLastReadTime(userId);
        if (readTime == null) {
            readTime = new Date(0L);
        }

        int unreadPosts;
        int unreadReplies;
        if (ROLE_MANAGER.equals(role)) {
            unreadPosts = eduPadMapper.countUnreadForumPostsAll(readTime, userId);
            unreadReplies = eduPadMapper.countUnreadForumRepliesAll(readTime, userId);
        } else {
            String className = getCurrentClassName();
            unreadPosts = eduPadMapper.countUnreadForumPostsByRole(role, className, readTime, userId);
            unreadReplies = eduPadMapper.countUnreadForumRepliesByRole(role, className, readTime, userId);
        }

        AjaxResult result = AjaxResult.success();
        result.put("unreadPosts", unreadPosts);
        result.put("unreadReplies", unreadReplies);
        result.put("unreadTotal", unreadPosts + unreadReplies);
        return result;
    }

    @PostMapping("/forum/notice/read")
    public AjaxResult markForumRead() {
        Long userId = SecurityUtils.getUserId();
        Date now = new Date();
        Date existing = eduPadMapper.selectForumLastReadTime(userId);
        if (existing == null) {
            eduPadMapper.insertForumReadState(userId, now);
        } else {
            eduPadMapper.updateForumReadState(userId, now);
        }
        return success();
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/review/ai-suggest")
    public AjaxResult aiSuggestReview(@RequestBody Map<String, Object> body) {
        String targetAnswer = body == null ? "" : String.valueOf(body.getOrDefault("targetAnswer", "")).trim();
        if (StringUtils.isEmpty(targetAnswer)) {
            return error("待批改答案不能为空");
        }
        String exampleAnswer = body == null ? "" : String.valueOf(body.getOrDefault("exampleAnswer", "")).trim();
        String exampleFeedback = body == null ? "" : String.valueOf(body.getOrDefault("exampleFeedback", "")).trim();
        int exampleScore = toInt(body == null ? null : body.get("exampleScore"), DEFAULT_EXAMPLE_SCORE);
        int maxScore = toInt(body == null ? null : body.get("maxScore"), DEFAULT_EXAM_MAX_SCORE);
        if (maxScore <= 0) {
            maxScore = DEFAULT_EXAM_MAX_SCORE;
        }
        if (exampleScore < 0) {
            exampleScore = 0;
        }
        if (exampleScore > maxScore) {
            exampleScore = maxScore;
        }

        double similarity = computeTextSimilarity(exampleAnswer, targetAnswer);
        double ratio = 0.55 + 0.45 * similarity;
        int suggestedScore;
        if (StringUtils.isEmpty(exampleAnswer)) {
            suggestedScore = Math.min(maxScore, Math.max(MIN_AI_FALLBACK_SCORE, targetAnswer.length() / 8));
        } else {
            suggestedScore = (int) Math.round(exampleScore * ratio);
        }
        suggestedScore = Math.max(0, Math.min(maxScore, suggestedScore));
        String level;
        if (suggestedScore >= (int) (maxScore * 0.9)) {
            level = "优秀";
        } else if (suggestedScore >= (int) (maxScore * 0.75)) {
            level = "良好";
        } else if (suggestedScore >= (int) (maxScore * 0.6)) {
            level = "合格";
        } else {
            level = "需改进";
        }

        String feedback;
        if (StringUtils.isEmpty(exampleFeedback)) {
            feedback = "AI建议：" + level + "。建议完善答题步骤、关键依据与最终结论。";
        } else {
            feedback = "AI参考批语（可人工修改）：" + exampleFeedback + "；综合判定：" + level + "。";
        }

        AjaxResult result = AjaxResult.success();
        result.put("suggestedScore", suggestedScore);
        result.put("suggestedFeedback", feedback);
        result.put("similarity", Math.round(similarity * 100.0) / 100.0);
        return result;
    }

    private String registerPadUser(EduRegisterBody registerBody) {
        String username = registerBody.getUsername();
        String password = registerBody.getPassword();
        String roleKey = normalizeRegisterRoleKey(registerBody.getRoleKey());
        Integer gradeNo = registerBody.getGradeNo();
        Integer classNo = registerBody.getClassNo();
        SysUser sysUser = new SysUser();
        sysUser.setUserName(username);

        if (StringUtils.isEmpty(username)) {
            return "用户名不能为空";
        }
        if (StringUtils.isEmpty(password)) {
            return "用户密码不能为空";
        }
        if (StringUtils.isEmpty(roleKey)) {
            return "注册角色无效，仅支持 teacher 或 student";
        }
        if (!isValidGradeClass(gradeNo, classNo)) {
            return "请选择正确的年级和班级（年级1-5，班级1-10）";
        }
        if (username.length() < UserConstants.USERNAME_MIN_LENGTH || username.length() > UserConstants.USERNAME_MAX_LENGTH) {
            return "账户长度必须在2到20个字符之间";
        }
        if (password.length() < UserConstants.PASSWORD_MIN_LENGTH || password.length() > UserConstants.PASSWORD_MAX_LENGTH) {
            return "密码长度必须在5到20个字符之间";
        }
        if (!userService.checkUserNameUnique(sysUser)) {
            return "保存用户'" + username + "'失败，注册账号已存在";
        }

        SysRole role = roleMapper.checkRoleKeyUnique(roleKey);
        if (role == null) {
            return "注册失败，系统未配置角色：" + roleKey;
        }
        if (!"0".equals(role.getStatus())) {
            return "注册失败，角色已停用：" + roleKey;
        }

        sysUser.setNickName(username);
        sysUser.setPwdUpdateDate(DateUtils.getNowDate());
        sysUser.setPassword(SecurityUtils.encryptPassword(password));
        sysUser.setRoleIds(new Long[] { role.getRoleId() });

        boolean success = userService.registerUser(sysUser);
        if (!success) {
            return "注册失败,请联系系统管理人员";
        }

        SysUser created = userService.selectUserByUserName(username);
        if (created == null || created.getUserId() == null) {
            return "注册失败，无法获取用户信息";
        }
        String className = buildClassName(gradeNo, classNo);
        int rows = eduPadMapper.upsertUserClassProfile(
                created.getUserId(),
                roleKey,
                gradeNo,
                classNo,
                className,
                ROLE_KEY_TEACHER.equals(roleKey) ? 1 : 0);
        if (rows <= 0) {
            return "注册失败，班级信息写入失败";
        }
        return "";
    }

    private boolean validateClassOnLogin(Long userId, Integer gradeNo, Integer classNo) {
        Map<String, Object> profile = eduPadMapper.selectUserClassProfileByUserId(userId);
        if (profile == null || profile.isEmpty()) {
            String roleKey = resolveUserRoleKey(userId);
            if (StringUtils.isEmpty(roleKey)) {
                return false;
            }
            int rows = eduPadMapper.upsertUserClassProfile(
                    userId,
                    roleKey,
                    gradeNo,
                    classNo,
                    buildClassName(gradeNo, classNo),
                    ROLE_KEY_TEACHER.equals(roleKey) ? 1 : 0
            );
            return rows > 0;
        }
        Object pGrade = profile.get(GRADE_NO_KEY);
        Object pClass = profile.get(CLASS_NO_KEY);
        if (!(pGrade instanceof Number) || !(pClass instanceof Number)) {
            return false;
        }
        return ((Number) pGrade).intValue() == gradeNo.intValue()
                && ((Number) pClass).intValue() == classNo.intValue();
    }

    private String resolveUserRoleKey(Long userId) {
        for (SysRole role : roleMapper.selectRolePermissionByUserId(userId)) {
            if (ROLE_KEY_TEACHER.equalsIgnoreCase(role.getRoleKey())) {
                return ROLE_KEY_TEACHER;
            }
            if (ROLE_KEY_STUDENT.equalsIgnoreCase(role.getRoleKey()) || ROLE_KEY_DEFAULT_STUDENT.equalsIgnoreCase(role.getRoleKey())) {
                return ROLE_KEY_STUDENT;
            }
        }
        return "";
    }

    private String normalizeRegisterRoleKey(String roleKey) {
        String normalized = StringUtils.trimToEmpty(roleKey).toLowerCase();
        if (ROLE_KEY_TEACHER.equals(normalized)) {
            return ROLE_KEY_TEACHER;
        }
        if (ROLE_KEY_STUDENT.equals(normalized)) {
            return ROLE_KEY_STUDENT;
        }
        return "";
    }

    private boolean isValidGradeClass(Integer gradeNo, Integer classNo) {
        if (gradeNo == null || classNo == null) {
            return false;
        }
        return gradeNo >= MIN_GRADE_NO && gradeNo <= MAX_GRADE_NO
                && classNo >= MIN_CLASS_NO && classNo <= MAX_CLASS_NO;
    }

    private String buildClassName(Integer gradeNo, Integer classNo) {
        return "G" + gradeNo + "-C" + classNo;
    }

    private void fillTeacherInfo(EduHomework homework) {
        homework.setTeacherId(currentUserId());
        homework.setTeacherName(currentUserNickName());
    }

    private void notifyHomeworkReviewed(Map<String, Object> current, EduHomeworkSubmission submission) {
        if (current == null || submission == null) {
            return;
        }
        Long studentId = toLong(current.get("student_id"));
        if (studentId == null || studentId <= 0) {
            return;
        }
        String className = String.valueOf(current.getOrDefault("class_name", ""));
        String homeworkTitle = String.valueOf(current.getOrDefault("homework_title", "作业"));
        String feedback = StringUtils.trimToEmpty(submission.getFeedback())
                .replaceAll("\\n?\\[REVIEW_IMAGE\\]\\(([^)\\s]+)\\)\\s*", "")
                .trim();
        String brief = StringUtils.isEmpty(feedback)
                ? ""
                : "，评语：" + StringUtils.substring(feedback, 0, 40);
        String msgContent = "你的《" + homeworkTitle + "》已批改，分数：" + submission.getScore() + brief;
        try {
            EduForumPost msg = new EduForumPost();
            msg.setTitle(CHAT_DM_TITLE);
            msg.setContent(msgContent);
            msg.setAuthorId(currentUserId());
            msg.setAuthorName(currentUserNickName());
            msg.setAuthorRole(resolveCurrentForumRole());
            msg.setTargetRole(String.valueOf(studentId));
            msg.setClassName(className);
            eduPadMapper.insertForumPost(msg);
        } catch (Exception ex) {
            log.warn("作业批改消息发送失败: submissionId={}, studentId={}, reason={}",
                    submission.getSubmissionId(), studentId, ex.getMessage());
        }
    }

    private String resolveCurrentForumRole() {
        List<SysRole> roles = roleMapper.selectRolePermissionByUserId(SecurityUtils.getUserId());
        if (roles != null) {
            for (SysRole role : roles) {
                String roleKey = role.getRoleKey();
                if ("admin".equalsIgnoreCase(roleKey) || "manager".equalsIgnoreCase(roleKey)) {
                    return ROLE_MANAGER;
                }
            }
            for (SysRole role : roles) {
                if (ROLE_KEY_TEACHER.equalsIgnoreCase(role.getRoleKey())) {
                    return ROLE_TEACHER;
                }
            }
        }
        return ROLE_STUDENT;
    }

    private String normalizeTargetRole(String targetRole, String currentRole) {
        String normalized = targetRole == null ? ROLE_ALL : targetRole.trim().toUpperCase();
        if (normalized.isEmpty()) {
            normalized = ROLE_ALL;
        }
        if (!(ROLE_ALL.equals(normalized) || ROLE_MANAGER.equals(normalized) || ROLE_TEACHER.equals(normalized) || ROLE_STUDENT.equals(normalized))) {
            return null;
        }
        if (ROLE_MANAGER.equals(currentRole)) {
            return normalized;
        }
        if (ROLE_TEACHER.equals(currentRole)) {
            if (!(ROLE_STUDENT.equals(normalized) || ROLE_ALL.equals(normalized))) {
                return null;
            }
            return normalized;
        }
        if (ROLE_STUDENT.equals(currentRole)) {
            if (ROLE_TEACHER.equals(normalized) || ROLE_ALL.equals(normalized)) {
                return normalized;
            }
            return null;
        }
        return ROLE_ALL;
    }

    private boolean isTeacherRole() {
        List<SysRole> roles = roleMapper.selectRolePermissionByUserId(SecurityUtils.getUserId());
        if (roles == null) {
            return false;
        }
        return roles.stream().anyMatch(role -> ROLE_KEY_TEACHER.equalsIgnoreCase(role.getRoleKey()));
    }

    private String getCurrentClassName() {
        Map<String, Object> profile = eduPadMapper.selectUserClassProfileByUserId(SecurityUtils.getUserId());
        if (profile == null) {
            return null;
        }
        Object className = profile.get(CLASS_NAME_KEY);
        return className == null ? null : String.valueOf(className);
    }

    private boolean canChatWith(Long peerUserId) {
        Long currentUserId = SecurityUtils.getUserId();
        if (peerUserId == null || currentUserId.equals(peerUserId)) {
            return false;
        }
        Map<String, Object> current = eduPadMapper.selectUserClassProfileByUserId(currentUserId);
        Map<String, Object> peer = eduPadMapper.selectUserClassProfileByUserId(peerUserId);
        if (current == null || peer == null) {
            return false;
        }
        String currentClassName = String.valueOf(current.get(CLASS_NAME_KEY));
        String peerClassName = String.valueOf(peer.get(CLASS_NAME_KEY));
        if (StringUtils.isEmpty(currentClassName) || !currentClassName.equals(peerClassName)) {
            return false;
        }
        String currentRole = String.valueOf(current.get(ROLE_KEY_KEY));
        String peerRole = String.valueOf(peer.get(ROLE_KEY_KEY));
        return (ROLE_KEY_TEACHER.equalsIgnoreCase(currentRole) && ROLE_KEY_STUDENT.equalsIgnoreCase(peerRole))
                || (ROLE_KEY_STUDENT.equalsIgnoreCase(currentRole) && ROLE_KEY_TEACHER.equalsIgnoreCase(peerRole));
    }

    private Long currentUserId() {
        return SecurityUtils.getUserId();
    }

    private String currentUserNickName() {
        return SecurityUtils.getLoginUser().getUser().getNickName();
    }

    private AjaxResult emptyListSuccess() {
        return success(Collections.emptyList());
    }

    private int toInt(Object value, int defaultValue) {
        if (value == null) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (Exception ex) {
            return defaultValue;
        }
    }

    private Long toLong(Object value) {
        if (value == null) {
            return null;
        }
        try {
            return Long.parseLong(String.valueOf(value));
        } catch (Exception ex) {
            return null;
        }
    }

    private double computeTextSimilarity(String a, String b) {
        if (StringUtils.isEmpty(a) || StringUtils.isEmpty(b)) {
            return 0.0;
        }
        Set<String> gramsA = buildBigrams(a);
        Set<String> gramsB = buildBigrams(b);
        if (gramsA.isEmpty() || gramsB.isEmpty()) {
            return 0.0;
        }
        int inter = 0;
        for (String item : gramsA) {
            if (gramsB.contains(item)) {
                inter++;
            }
        }
        return (2.0 * inter) / (gramsA.size() + gramsB.size());
    }

    private Set<String> buildBigrams(String s) {
        Set<String> set = new HashSet<>();
        String raw = s.replaceAll("\\s+", "");
        if (raw.length() < 2) {
            if (!raw.isEmpty()) {
                set.add(raw);
            }
            return set;
        }
        for (int i = 0; i < raw.length() - 1; i++) {
            set.add(raw.substring(i, i + 2));
        }
        return set;
    }
}
