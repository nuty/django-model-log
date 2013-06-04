django-model-log
================

a simple django model modify log app

referenced to django-dirtyfields app

https://github.com/smn/django-dirtyfields

class:
      Log
属性：
    ADDITION    #添加
    CHANGE      #修改
    DELETION    #删除

类方法: 
      set_log(cls,args,.....)

      描述：
         生成日志的主方法

      参数: 
        request 
            request对象。（非必须）
        obj
            修改的某个对象。（必须）
        action
            修改的方式。（必须）
        user=None
            执行操作的用户（非必须）
        change_message=None
            操作的文字信息（非必须）

       注意事项：
         request参数 和 user参数两者必须填写一项。

       使用实例：
         from common.models import Log
         from app.food.models import Food
         food = Food()
         Log.set_log(request,food,Log.ADDITION)
         上例是生成了一个 某用户添加了一个广告的日志。

         如果request == None 那么：
         from django.contrib.auth.models import User
         user = User()          
         Log.set_log(request=None,obj=food,action=Log.ADDITION,user=user)

         函数会根据你的action参数自动生成change_message,例如 Log.ADDITION 是 创建了，Log.CHANGE 是 修改了，Log.DELETION 是 删除了。
         如果使用自己的修改信息，请在生成日志的时候填写change_message 参数。例如：

         Log.set_log(request=None,obj=food,action=Log.DELETION,user=user,change_message='balallalala ..........')


      get_log(cls,args,.....)
          描述：
            获取生成的日志

          参数: 
            user=None (非必须)
               要获取的某位用户的操作记录
            model=None
               要获取的某个models的操作记录
            app=None
               要获取的某个app的操作记录
            action=None
               要获取的某种操作方式的操作记录
            count=500 
               获得记录的条数，默认是500条，可根据自己需要填写
          
          注意事项：
             获得的记录已经按照时间排序完成，最新生成的会默认排在上面。
             获取聚合记录时请把参数放到列表里
          
          使用实例：
             from app.common.models import Log
             logs = Log.get_log(user=request.user,app='food',action=Log.ADDITION,count=1000)    ## 获得1000条ad app 属于当前user的 添加操作记录 (不写参数会获得所有的日志)
             logs = Log.get_log(app='food')   ##获得 hotel app的所有操作日志
             logs = Log.get_log(app='food',model='Info')   ##获得 app hotel 的Info模型的操作日志
             logs = Log.get_log(app=['food','food'])   ##获得 app food 和 food 的操作日志
             logs = Log.get_log(app=['food','ball'],model=['Info','Room'])   ##获得 app food 和 ball 下的Info和Room 模型的操作日志
             logs = Log.get_log(model=['Info','Room'])   ##获得 Info和Room 模型的操作日志

出错信息：
       正常情况下只会在调用set_log的时候出错.
       ValueError('you must take argument request or user') ##当你request参数和user参数都没有填写的时候。
       
       TypeError('require model instance argument obj') ##当你没有填写 obj参数的时候。

       TypeError('require a integer argument action')  ##当你没有填写action 参数的时候。