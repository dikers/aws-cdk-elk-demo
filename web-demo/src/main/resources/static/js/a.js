var vue ;
$(function(){
    vue = new Vue({
            el: '#main',
            data:{
                amount:5,
                total_count:0,
                log_text_area: '',
            },methods:{
                 send:function(){
                    getData()
                 }
            }
    })
});


function getData(){
        _amount = parseInt(vue.amount);
        vue.amount = _amount
      $.ajax({
              async:true,
              type:"get",
              contentType : "application/json;charset=UTF-8", //类型必填
              url:"send?total="+_amount,
              dataType:"json",
              success:function(data){
                   console.log(data);
                   vue.total_count += data.count
                   vue.log_text_area  += '\n' + data.time +'  发送了'+data.count+'条日志  总计： '+vue.total_count

              },
              error:function(data){
                  console.log(data.result);
              }
     })

}
