from django.db import models

OPLOG_TYPE_CHOICE = (
	(0, u'新增广告')，
	(1, u'编辑广告')，
	(2, u'删除广告')，
	(3, u'调整广告顺序')，
	(4, u'新增应用')，
	(5, u'编辑应用')，
	(6, u'删除应用')，
	(7, u'上线应用')，
	(8, u'下线应用')，
	(9, u'新增应用专题')，
	(10, u'编辑应用专题')，
	(11, u'删除应用专题')，
	(12, u'上线应用专题')，
	(13, u'下线应用专题')，
	(14, u'调整应用专题顺序')，
	(15, u'新增大区')，
	(16, u'编辑大区')，
	(17, u'删除大区')，
	(18, u'新增公司')，
	(19, u'编辑公司')，
	(20, u'删除公司')，
	(21, u'新增门店')，
	(22, u'编辑门店')，
	(23, u'删除门店')，
	(24, u'新增用户组')，
	(25, u'编辑用户组')，
	(26, u'删除用户组')，
	(27, u'新增用户')，
	(28, u'编辑用户')，
	(29, u'删除用户')，
	(30, u'修改用户密码')，
	(31, u'新增管理员')，
	(32, u'编辑管理员')，
	(33, u'删除管理员')，
	(34, u'重置密码')，
	)

# Create your models here.
class op_log(models.Model):
    date = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=32)
    type = models.IntegerField(choices = OPLOG_TYPE_CHOICE)
    content = models.CharField(max_length=80)
    class Meta:
        ordering = ('-pk',)