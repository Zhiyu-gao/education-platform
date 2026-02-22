package com.ruoyi.student.controller;

import java.util.Date;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.student.domain.EduExam;
import com.ruoyi.student.domain.EduExamScore;
import com.ruoyi.student.domain.EduForumPost;
import com.ruoyi.student.domain.EduForumReply;
import com.ruoyi.student.domain.EduHomework;
import com.ruoyi.student.domain.EduHomeworkSubmission;
import com.ruoyi.student.domain.EduTeacherTask;
import com.ruoyi.student.mapper.EduPadMapper;
import com.ruoyi.system.mapper.SysRoleMapper;
import com.ruoyi.common.core.domain.entity.SysRole;

@RestController
@RequestMapping("/education/pad")
public class EduPadController extends BaseController {
    private static final String ROLE_MANAGER = "MANAGER";
    private static final String ROLE_TEACHER = "TEACHER";
    private static final String ROLE_STUDENT = "STUDENT";
    private static final String ROLE_ALL = "ALL";

    @Autowired
    private EduPadMapper eduPadMapper;

    @Autowired
    private SysRoleMapper roleMapper;

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
            homework.setStatus("PUBLISHED");
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
            return success(new ArrayList<>());
        }
        return success(eduPadMapper.selectHomeworkByClassName(className));
    }

    @PreAuthorize("@ss.hasRole('student')")
    @PostMapping("/homework/{homeworkId}/submit")
    public AjaxResult submitHomework(@PathVariable Long homeworkId, @RequestBody EduHomeworkSubmission submission) {
        Long studentId = SecurityUtils.getUserId();
        Long exists = eduPadMapper.selectHomeworkSubmissionExists(homeworkId, studentId);
        if (exists != null) {
            return error("该作业已提交，无需重复提交");
        }
        submission.setHomeworkId(homeworkId);
        submission.setStudentId(studentId);
        submission.setStudentName(SecurityUtils.getLoginUser().getUser().getNickName());
        submission.setSubmitTime(new Date());
        return toAjax(eduPadMapper.insertHomeworkSubmission(submission));
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
        if (submission.getScore() == null || submission.getScore() < 0 || submission.getScore() > 100) {
            return error("作业分数必须在0-100之间");
        }
        Map<String, Object> current = eduPadMapper.selectHomeworkSubmissionById(submission.getSubmissionId());
        if (current == null || current.isEmpty()) {
            return error("提交记录不存在");
        }
        Object teacherIdObj = current.get("teacher_id");
        if (!(teacherIdObj instanceof Number) || ((Number) teacherIdObj).longValue() != SecurityUtils.getUserId()) {
            return error("只能批改自己发布作业的提交");
        }
        return toAjax(eduPadMapper.updateHomeworkSubmissionScore(submission));
    }

    @PreAuthorize("@ss.hasRole('teacher') or @ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/exam")
    public AjaxResult createExam(@Validated @RequestBody EduExam exam) {
        exam.setTeacherId(SecurityUtils.getUserId());
        exam.setTeacherName(SecurityUtils.getLoginUser().getUser().getNickName());
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
            return success(new ArrayList<>());
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
        examScore.setStudentId(SecurityUtils.getUserId());
        examScore.setStudentName(SecurityUtils.getLoginUser().getUser().getNickName());
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
        result.put("examScores", eduPadMapper.selectExamScoreByStudentId(SecurityUtils.getUserId()));
        String className = getCurrentClassName();
        if (StringUtils.isEmpty(className)) {
            result.put("performanceScores", new ArrayList<>());
        } else {
            result.put("performanceScores", eduPadMapper.selectStudentPerformanceByClassName(className));
        }
        return result;
    }

    @PreAuthorize("@ss.hasRole('admin') or @ss.hasRole('manager')")
    @PostMapping("/manager/teacher-task")
    public AjaxResult createTeacherTask(@Validated @RequestBody EduTeacherTask task) {
        if (task.getStatus() == null) {
            task.setStatus("TODO");
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
            return success(new ArrayList<>());
        }
        return success(eduPadMapper.selectStudentPerformanceByClassName(className));
    }

    @GetMapping("/forum/posts")
    public AjaxResult listForumPosts() {
        String role = resolveCurrentForumRole();
        String className = getCurrentClassName();
        List<Map<String, Object>> posts = ROLE_MANAGER.equals(role)
                ? eduPadMapper.selectForumPostsAll()
                : eduPadMapper.selectForumPostsByRole(role, className);

        if (posts == null || posts.isEmpty()) {
            return success(new ArrayList<>());
        }

        List<Long> postIds = posts.stream()
                .map(item -> Long.valueOf(String.valueOf(item.get("post_id"))))
                .collect(Collectors.toList());
        List<Map<String, Object>> replies = eduPadMapper.selectForumRepliesByPostIds(postIds);
        Map<Long, List<Map<String, Object>>> replyMap = new HashMap<>();
        if (replies != null) {
            for (Map<String, Object> reply : replies) {
                Long postId = Long.valueOf(String.valueOf(reply.get("post_id")));
                replyMap.computeIfAbsent(postId, key -> new ArrayList<>()).add(reply);
            }
        }

        for (Map<String, Object> post : posts) {
            Long postId = Long.valueOf(String.valueOf(post.get("post_id")));
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

        post.setAuthorId(SecurityUtils.getUserId());
        post.setAuthorName(SecurityUtils.getLoginUser().getUser().getNickName());
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
        reply.setAuthorId(SecurityUtils.getUserId());
        reply.setAuthorName(SecurityUtils.getLoginUser().getUser().getNickName());
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

    private void fillTeacherInfo(EduHomework homework) {
        homework.setTeacherId(SecurityUtils.getUserId());
        homework.setTeacherName(SecurityUtils.getLoginUser().getUser().getNickName());
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
                if ("teacher".equalsIgnoreCase(role.getRoleKey())) {
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
        return roles.stream().anyMatch(role -> "teacher".equalsIgnoreCase(role.getRoleKey()));
    }

    private String getCurrentClassName() {
        Map<String, Object> profile = eduPadMapper.selectUserClassProfileByUserId(SecurityUtils.getUserId());
        if (profile == null) {
            return null;
        }
        Object className = profile.get("class_name");
        return className == null ? null : String.valueOf(className);
    }
}
