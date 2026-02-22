package com.ruoyi.student.domain;

import java.util.Date;

public class EduForumReply
{
    private Long replyId;
    private Long postId;
    private String content;
    private Long authorId;
    private String authorName;
    private String authorRole;
    private Date createTime;

    public Long getReplyId()
    {
        return replyId;
    }

    public void setReplyId(Long replyId)
    {
        this.replyId = replyId;
    }

    public Long getPostId()
    {
        return postId;
    }

    public void setPostId(Long postId)
    {
        this.postId = postId;
    }

    public String getContent()
    {
        return content;
    }

    public void setContent(String content)
    {
        this.content = content;
    }

    public Long getAuthorId()
    {
        return authorId;
    }

    public void setAuthorId(Long authorId)
    {
        this.authorId = authorId;
    }

    public String getAuthorName()
    {
        return authorName;
    }

    public void setAuthorName(String authorName)
    {
        this.authorName = authorName;
    }

    public String getAuthorRole()
    {
        return authorRole;
    }

    public void setAuthorRole(String authorRole)
    {
        this.authorRole = authorRole;
    }

    public Date getCreateTime()
    {
        return createTime;
    }

    public void setCreateTime(Date createTime)
    {
        this.createTime = createTime;
    }
}
