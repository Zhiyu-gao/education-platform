
package com.ruoyi.student.controller;

import java.util.List;
import javax.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.common.utils.file.FileUploadUtils;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.student.controller.CustomBaseController;
import com.ruoyi.student.domain.StudentPerformance;
import com.ruoyi.student.service.IStudentPerformanceService;

/**
 * 学生成绩表现 信息操作处理
 * 
 * @author ruoyi
 */
@RestController
@RequestMapping("/student/performance")
public class StudentPerformanceController extends CustomBaseController
{
    private static final Logger log = LoggerFactory.getLogger(StudentPerformanceController.class);

    @Autowired
    private IStudentPerformanceService studentPerformanceService;

    /**
     * 获取学生成绩表现列表
     */
    // 使用@Anonymous注解允许匿名访问，完全绕过权限检查
    @Anonymous
    @GetMapping("/list")
    public TableDataInfo list(StudentPerformance studentPerformance)
    {
        startPage();
        List<StudentPerformance> list = studentPerformanceService.selectStudentPerformanceList(studentPerformance);
        return getDataTable(list);
    }

    /**
     * 导出学生成绩表现数据
     */
    @PreAuthorize("@ss.hasPermi('student:performance:export')")
    @Log(title = "学生成绩管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, StudentPerformance studentPerformance)
    {
        List<StudentPerformance> list = studentPerformanceService.exportStudentPerformance(studentPerformance);
        ExcelUtil<StudentPerformance> util = new ExcelUtil<StudentPerformance>(StudentPerformance.class);
        util.exportExcel(response, list, "学生成绩数据");
    }

    /**
     * 根据ID获取学生成绩表现详细信息
     */
    @Anonymous
    @GetMapping(value = "/{id}")
    public AjaxResult getInfo(@PathVariable("id") Long id)
    {
        return success(studentPerformanceService.selectStudentPerformanceById(id));
    }

    /**
     * 新增学生成绩表现
     */
    @Anonymous
    @Log(title = "学生成绩管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@Validated @RequestBody StudentPerformance studentPerformance)
    {
        return toAjax(studentPerformanceService.insertStudentPerformance(studentPerformance));
    }

    /**
     * 修改学生成绩表现
     */
    @PreAuthorize("@ss.hasPermi('student:performance:edit')")
    @Log(title = "学生成绩管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@Validated @RequestBody StudentPerformance studentPerformance)
    {
        return toAjax(studentPerformanceService.updateStudentPerformance(studentPerformance));
    }

    /**
     * 删除学生成绩表现
     */
    @PreAuthorize("@ss.hasPermi('student:performance:remove')")
    @Log(title = "学生成绩管理", businessType = BusinessType.DELETE)
    @DeleteMapping("/{ids}")
    public AjaxResult remove(@PathVariable Long[] ids)
    {
        return toAjax(studentPerformanceService.deleteStudentPerformanceByIds(ids));
    }

    /**
     * 导入学生成绩表现数据
     */
    @PreAuthorize("@ss.hasPermi('student:performance:import')")
    @Log(title = "学生成绩管理", businessType = BusinessType.IMPORT)
    @PostMapping("/importData")
    public AjaxResult importData(MultipartFile file, boolean updateSupport)
    {
        try
        {
            // 上传文件到临时目录
            String filePath = FileUploadUtils.upload(file);
            String result = studentPerformanceService.importStudentPerformance(filePath);
            if (StringUtils.isNotEmpty(result))
            {
                return error(result);
            }
            return success("导入成功");
        }
        catch (Exception e)
        {
            log.error("导入失败", e);
            return error("导入失败：" + e.getMessage());
        }
    }

    /**
     * 下载导入模板
     */
    @PreAuthorize("@ss.hasPermi('student:performance:import')")
    @GetMapping("/importTemplate")
    public void importTemplate(HttpServletResponse response)
    {
        ExcelUtil<StudentPerformance> util = new ExcelUtil<StudentPerformance>(StudentPerformance.class);
        util.importTemplateExcel(response, "学生成绩数据");
    }
}
