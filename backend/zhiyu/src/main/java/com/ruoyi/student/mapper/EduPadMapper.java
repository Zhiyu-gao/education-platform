package com.ruoyi.student.mapper;

import java.util.Date;
import java.util.List;
import java.util.Map;
import org.apache.ibatis.annotations.Param;
import com.ruoyi.student.domain.EduExam;
import com.ruoyi.student.domain.EduExamScore;
import com.ruoyi.student.domain.EduForumPost;
import com.ruoyi.student.domain.EduForumReply;
import com.ruoyi.student.domain.EduHomework;
import com.ruoyi.student.domain.EduHomeworkSubmission;
import com.ruoyi.student.domain.EduTeacherTask;

public interface EduPadMapper {
    int insertHomework(EduHomework homework);
    List<EduHomework> selectHomeworkByTeacherId(Long teacherId);
    List<EduHomework> selectHomeworkAll();
    List<EduHomework> selectHomeworkByClassName(String className);

    int insertHomeworkSubmission(EduHomeworkSubmission submission);
    List<Map<String, Object>> selectHomeworkSubmissionByTeacherId(Long teacherId);
    List<Map<String, Object>> selectHomeworkSubmissionByStudentId(Long studentId);
    Map<String, Object> selectHomeworkSubmissionById(Long submissionId);
    int updateHomeworkSubmissionScore(EduHomeworkSubmission submission);

    int insertExam(EduExam exam);
    List<EduExam> selectExamByTeacherId(Long teacherId);
    List<EduExam> selectExamAll();
    List<EduExam> selectExamByClassName(String className);
    EduExam selectExamById(Long examId);

    int upsertExamScore(EduExamScore examScore);
    List<Map<String, Object>> selectExamScoreByTeacherId(Long teacherId);
    List<Map<String, Object>> selectExamScoreByStudentId(Long studentId);
    List<Map<String, Object>> selectExamScoreAll();

    int insertTeacherTask(EduTeacherTask task);
    List<EduTeacherTask> selectTeacherTaskByTeacherId(Long teacherId);

    List<Map<String, Object>> selectStudentPerformanceAll();
    List<Map<String, Object>> selectStudentPerformanceByClassName(String className);
    List<Map<String, Object>> selectStudentPerformanceByStudentId(Long studentId);

    Long selectHomeworkSubmissionExists(@Param("homeworkId") Long homeworkId, @Param("studentId") Long studentId);

    int insertForumPost(EduForumPost post);
    List<Map<String, Object>> selectForumPostsByRole(@Param("role") String role, @Param("className") String className);
    List<Map<String, Object>> selectForumPostsAll();
    int insertForumReply(EduForumReply reply);
    List<Map<String, Object>> selectForumRepliesByPostIds(@Param("postIds") List<Long> postIds);
    List<Map<String, Object>> selectClassChatContacts(@Param("className") String className, @Param("excludeUserId") Long excludeUserId, @Param("roleKey") String roleKey);
    List<Map<String, Object>> selectChatMessages(@Param("className") String className, @Param("currentUserId") Long currentUserId, @Param("peerUserId") Long peerUserId, @Param("currentUserIdStr") String currentUserIdStr, @Param("peerUserIdStr") String peerUserIdStr);
    List<Map<String, Object>> selectGroupChatMessages(@Param("className") String className, @Param("groupId") String groupId);

    Date selectForumLastReadTime(Long userId);
    int insertForumReadState(@Param("userId") Long userId, @Param("readTime") Date readTime);
    int updateForumReadState(@Param("userId") Long userId, @Param("readTime") Date readTime);
    int countUnreadForumPostsByRole(@Param("role") String role, @Param("className") String className, @Param("readTime") Date readTime, @Param("userId") Long userId);
    int countUnreadForumPostsAll(@Param("readTime") Date readTime, @Param("userId") Long userId);
    int countUnreadForumRepliesByRole(@Param("role") String role, @Param("className") String className, @Param("readTime") Date readTime, @Param("userId") Long userId);
    int countUnreadForumRepliesAll(@Param("readTime") Date readTime, @Param("userId") Long userId);

    Map<String, Object> selectUserClassProfileByUserId(Long userId);
    int upsertUserClassProfile(@Param("userId") Long userId, @Param("roleKey") String roleKey, @Param("gradeNo") Integer gradeNo, @Param("classNo") Integer classNo, @Param("className") String className, @Param("headTeacher") Integer headTeacher);
    Integer countStudentInClassByUserId(@Param("studentUserId") Long studentUserId, @Param("className") String className);
}
