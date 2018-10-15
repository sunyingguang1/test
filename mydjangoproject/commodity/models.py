from django.db import models

# class BookInfoManager(models.Manager):
#     def get_queryset(self):
#         return super(BookInfoManager, self).get_queryset().filter(isDelete=False)
# # Create your models here.
# #与数据库对应的实体类
# class BookInfo(models.Model):
#     #不需要定义主键列，在生成时会自动添加，并且值为自动增长
#     btitle =models.CharField(max_length=100)
#     bpubdate=models.DateTimeField(db_column='pub_date')#在数据库中的别名
#     bcommet=models.IntegerField(null=False)
#     isDelete=models.BooleanField(default=False)
#     class Meta:#元选项
#         db_table='bookinfo'#改数据库中表的名字
#         ordering=['id']#排序规则
#     book1=models.Manager()
#     book2=BookInfoManager()
# class HeroInfo(models.Model):
#     hname=models.CharField(max_length=100)
#     hgender=models.BooleanField(default=True)
#     isDelete=models.BooleanField(default=False)
#     hconcent=models.TextField()
#     hbookinfo=models.ForeignKey(BookInfo)
