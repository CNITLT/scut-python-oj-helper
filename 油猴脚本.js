// ==UserScript==
// @name         python oj辅助
// @namespace    http://tampermonkey.net/
// @version      2.8
// @description  辅助判断PYTHON的编程题答案
// @author       You
// @match        *://1024.se.scut.edu.cn/%E5%85%A8%E9%83%A8%E4%BD%9C%E4%B8%9A*
// @match        *://1024.se.scut.edu.cn/%e5%85%a8%e9%83%a8%e4%bd%9c%e4%b8%9a*
// @match        *://222.201.187.187:8006/%E5%85%A8%E9%83%A8%E4%BD%9C%E4%B8%9A*
// @match        *://222.201.187.187:8006/%e5%85%a8%e9%83%a8%e4%bd%9c%e4%b8%9a*
// @match        *://1024.se.scut.edu.cn/%E4%BD%9C%E4%B8%9A%E6%B1%87%E6%80%BB*
// @match        *://1024.se.scut.edu.cn/%e4%bd%9c%e4%b8%9a%e6%b1%87%e6%80%bb*
// @match        *://222.201.187.187:8006/%E4%BD%9C%E4%B8%9A%E6%B1%87%E6%80%BB*
// @match        *://222.201.187.187:8006/%e4%bd%9c%e4%b8%9a%e6%b1%87%e6%80%bb*
// @match        *://1024.se.scut.edu.cn/%E6%98%BE%E7%A4%BA%E8%AF%95%E5%8D%B7*
// @match        *://1024.se.scut.edu.cn/%e6%98%be%e7%a4%ba%e8%af%95%e5%8d%b7*
// @connect      *
// @grant        unsafeWindow
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';


    console.log("scut python OJ");
    //用于匹配 "全部作业"
    var all_homework_reg = /%E5%85%A8%E9%83%A8%E4%BD%9C%E4%B8%9A/i;
    //用于匹配 "作业汇总"
    var homework_summary_reg = /%E4%BD%9C%E4%B8%9A%E6%B1%87%E6%80%BB/i;
    //用于匹配 "显示试卷"
    var single_student_homework_page_reg = /%E6%98%BE%E7%A4%BA%E8%AF%95%E5%8D%B7/i;
    //这个必须在最开始运行，原始HTML页面数据必须保存，不然后端解析不了
    var originalPageHTML = document.documentElement.outerHTML;

    if(all_homework_reg.test(window.location.href)) {
        //批改部分的代码
        console.log("作业批改增强")
        class Student_info{
            constructor(info_dom, answer_dom,score_doms,remark_dom) {
                this.info_dom = info_dom;
                this.answer_dom = answer_dom;
                this.score_doms = score_doms;
                this.remark_dom = remark_dom;
                //补交作业没有提交时间
                let student_info_pattern = /(\d*) (.*) (\S*) 提交时间:(.*)/;
                let matchRes = info_dom.innerText.match(student_info_pattern);
                this.studentNumber = matchRes[1];
                this.studentName = matchRes[2];
                this.className = matchRes[3];
                this.submit_date = new Date(matchRes[4]);
                this.answer = answer_dom.innerText;

            }

            hidden(){
                this.info_dom.hidden = true;
                this.answer_dom.hidden = true;
                for(let i = 0; i < this.score_doms.length;i++){
                    this.score_doms[i].hidden = true;
                }
                this.remark_dom.hidden = true;
            }

            show(){
                this.info_dom.hidden = false;
                this.answer_dom.hidden = false;
                for(let i = 0; i < this.score_doms.length;i++){
                    this.score_doms[i].hidden = false;
                }
                this.remark_dom.hidden = false;
            }

            //返回分数索引，没有就返回-1
            getScoreIndex(){
                for(let i = 0; i < this.score_doms.length;i++){
                    if(this.score_doms[i].checked){
                        return i;
                    }
                }
                return -1;
            }

            setScoreByIndex(index){
                if(index>=0 && index < this.score_doms.length){
                    this.score_doms[index].checked = true;
                }
            }

            //返回评语
            getRemark(){
                return this.remark_dom.value;
            }

            setRemark(value){
                this.remark_dom.value = value;
            }

            backupScore(){
                let index = this.getScoreIndex();
                let remark_str =  this.getRemark();
                let backPattern =  /^back:\[(-?\d+)\]/;
                let new_remark_str ="back:[" + index.toString() + "]" + remark_str.replace(backPattern,"");
                this.setRemark(new_remark_str);
            }

            hasBackup(){
                let remark_str = this.getRemark();
                let backPattern = /^back:\[(-?\d+)\]/;
                return backPattern.test(remark_str);
            }

            restoreScore(){
                if(this.hasBackup()){
                    let backPattern = /^back:\[(-?\d+)\]/;
                    let remark_str = this.getRemark();
                    let backIndex = parseInt(remark_str.match(backPattern)[1]);
                    if(backIndex >= 0){
                        this.setScoreByIndex(backIndex);
                    }
                }
            }

            //获取评语的真实长度，不包含备份
            getRemarkRealLength(){
                let remark_str =  this.getRemark();
                let backPattern =  /^back:\[(-?\d+)\]/;
                let real_remark_str = remark_str.replace(backPattern,"");
                return real_remark_str.length;
            }
        }
        //必须在页面没改变前调用
        function get_student_info_list(){
            let font_arr = document.getElementsByTagName("font");
            let student_font_arr = new Array();
            //补交答案没有具体的提交时间
            let student_info_pattern = /(\d*) (.*) (\S*) 提交时间:(.*)/;
            let student_info_list = new Array();
            for(let i = 0; i < font_arr.length;i++) {
                let text = font_arr[i].innerText;
                if (student_info_pattern.test(text)) {
                    student_font_arr.push(font_arr[i]);
                }
            }
            let inputRadioList = Array.prototype.slice.call(document.querySelectorAll("input[type=radio][name^=radioScore]"));
            let studentNum = inputRadioList.length / 11;
            let studentCodeDomList = Array.prototype.slice.call(document.getElementsByClassName("divcss5-b")).slice(-1 * studentNum);
            let remarkList = Array.prototype.slice.call(document.querySelectorAll("input[type=text][id^=txtRemark]"));
            for(let i = 0; i < studentNum;i++){
                student_info_list.push(new Student_info(student_font_arr[i],studentCodeDomList[i],
                    inputRadioList.slice(i*11,(i+1)*11),remarkList[i]));
            }
            return student_info_list;
        }
        var student_list = get_student_info_list();
        unsafeWindow.student_list = student_list;

        var inputRadioNamePre = "radioScore";
        var inputRemarkIdPre = "txtRemark";
        //关联相同答案的得分和评语
        //先解析出答案和其对应的得分
        //在原有DOM没变之前解析
        //先获取分数的DOM部分
        var inputRadioList = document.querySelectorAll("input[type=radio]");
        var studentNum = inputRadioList.length / 11;
        var studentCodeDomList = Array.prototype.slice.call(document.getElementsByClassName("divcss5-b")).slice(-1 * studentNum);
        var codeDic = {};
        for (let i = 0; i < studentCodeDomList.length; i++) {
            let code = studentCodeDomList[i].innerText;
            if (!codeDic.hasOwnProperty(code)) {
                codeDic[code] = []
            }
            //获取后面数字部分的字符串
            codeDic[code].push(inputRadioList[i * 11].name.substring(inputRadioNamePre.length));
        }
        //遍历codeDic转化为数字标识:相同答案组的数字标识的字典
        var sameCodeDic = {};
        for (let key in codeDic) {
            let numIdArr = codeDic[key];
            for (let i = 0; i < numIdArr.length; i++) {
                sameCodeDic[numIdArr[i]] = numIdArr;
            }
        }

        //同步相同答案的分数
        function synInputRadio() {
            let dom = this;
            let value = dom.value;
            let name = dom.name;
            let num = name.substring(inputRadioNamePre.length);
            let numIdArr = sameCodeDic[num];
            console.log(numIdArr);
            for (let i = 0; i < numIdArr.length; i++) {
                let otherRadioName = inputRadioNamePre + numIdArr[i];
                let otherRadioList = document.getElementsByName(otherRadioName);
                for (let j = 0; j < otherRadioList.length; j++) {
                    let otherRadioDom = otherRadioList[j];
                    if (otherRadioDom.value == value) {
                        otherRadioDom.checked = true;
                    }
                }
            }
        }

        //给所有radio绑定同步函数
        for (let i = 0; i < inputRadioList.length; i++) {
            inputRadioList[i].addEventListener("click", synInputRadio.bind(inputRadioList[i]));
        }

        //同步评语的函数
        function synRemark() {
            let dom = this;
            let value = dom.value;
            let id = dom.id;
            let num = id.substring(inputRemarkIdPre.length);
            let numIdArr = sameCodeDic[num];
            for (let i = 0; i < numIdArr.length; i++) {
                let otherRemarkId = inputRemarkIdPre + numIdArr[i];
                let otherRemarkDom = document.getElementById(otherRemarkId);
                otherRemarkDom.value = value;
            }
        }

        //给input绑定同步评语函数
        for (let key in codeDic) {
            let numIdArr = codeDic[key];
            for (let i = 0; i < numIdArr.length; i++) {
                let remarkId = inputRemarkIdPre + numIdArr[i];
                let remarkDom = document.getElementById(remarkId);
                remarkDom.addEventListener("change", synRemark.bind(remarkDom));
            }
        }

        //打印没评价好的学生编号，没给分或给分了但评语不足5个
        function pfUnvalue() {
            for (let i = 0; i < inputRadioList.length; i += 11) {
                let value = undefined;
                //获取评语
                let num = inputRadioList[i].name.substring(inputRadioNamePre.length);
                let remarkId = inputRemarkIdPre + num;
                let remarkDom = document.getElementById(remarkId);
                let remark = remarkDom.value;
                for (let j = i; j < i + 11; j++) {
                    let radioDom = inputRadioList[j];
                    if (radioDom.checked == true) {
                        value = radioDom.value;
                        break;
                    }
                }

                //let length = remark.length;
                let backPattern =  /^back:\[(-?\d+)\]/;
                let real_remark_str = remark_str.replace(backPattern,"");
                let remark_length = real_remark_str.length;
                if (value == undefined || (value != 100 && remark_length < 5)) {
                    console.log(i / 11 + 1);
                    continue;
                }
            }
        }

        //暴露出去
        unsafeWindow.pfUnvalue = pfUnvalue;


        //只能在页面加载完后创建一次，不然会有bug
        class StudentsAnswerControler {
            constructor() {
                var studentNum = document.querySelectorAll("input[type=radio]").length / 11;
                this.answerDomList = [];
                // 获取所有学生的DIV DOM块，不包含案例
                this.studentDomList = Array.prototype.slice.call(document.getElementsByClassName("divcss5-b")).slice(-1 * studentNum);
                // 添加答案显示块
                for (let i = 0; i < this.studentDomList.length; i++) {
                    var divDom = this.studentDomList[i];
                    //创建div块，并插入
                    var newDom = divDom.cloneNode(true);
                    newDom.style = "float:right";
                    newDom.id = "answerRunRes"+i;
                    divDom.parentNode.insertBefore(newDom, divDom);
                    //清空代码
                    var answerDom = newDom.getElementsByTagName("code")[0];
                    answerDom.innerHTML = "";
                    //加入列表
                    this.answerDomList.push(answerDom);
                }
            }

            //重新设置下代码块的DOM大小，不然布局会乱套
            resizeStudentDom(index) {
                var studentDivDom = this.studentDomList[index];
                var answerDivDom = this.answerDomList[index].parentNode.parentNode;//两层parent后就是div的DOM元素
                if (studentDivDom.clientHeight < answerDivDom.clientHeight) {
                    studentDivDom.style = "height:" + answerDivDom.clientHeight.toString() + "px;"
                }
            }

            setAnswer(index, answer) {
                if (this.answerDomList[index].innerHTML == "") {
                    this.answerDomList[index].innerHTML = answer;
                } else {
                    this.answerDomList[index].innerHTML += "\n";
                    this.answerDomList[index].innerHTML += answer;
                }
                this.resizeStudentDom(index);
            }

            clearAnswer(index) {
                this.answerDomList[index].innerHTML = "";
                this.studentDomList[index].style = "";
            }

            getAnswer(index) {
                return this.answerDomList[index].innerHTML;
            }

            setAnswers(answers) {
                //案例可能有多个code块，需要跳过多出来的
                let skipNum = this.length - Object.keys(answers).length;
                for (let i = 0; i < this.length; i++) {
                    this.setAnswer(i + skipNum, answers[i]);
                }
            }

            clearAllAnswer() {
                for (let i = 0; i < students.length; i++) {
                    this.clearAnswer(i);
                }
            }

            get length() {
                return this.answerDomList.length;
            }
        }

        var students = new StudentsAnswerControler();

        function requestAnswer() {
            var input = document.getElementById("pythonWebOJTestInput").value;
            GM_xmlhttpRequest({
                method: "post",
                url: "http://localhost:8000/oj",
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                data: JSON.stringify({
                    "document": originalPageHTML,
                    "input": input
                }),
                onload: function (response) {
                    console.log(response.responseText);
                    //设置返回答案
                    var answers = JSON.parse(response.responseText);
                    students.setAnswers(answers);
                },
                onerror: function (response) {
                    console.log("请求失败");
                }
            });
        }

        //从这里开始改变DOM元素
        //针对部分中文符号进行检测主要是容易混用的符号
        for (let i = 0; i < studentCodeDomList.length; i++) {
            let code = studentCodeDomList[i].innerText;

            //部分中文符号匹配
            let chineseCharMatchRes = code.match(/[｛｝（）【】：“”‘’，。－＋＝]/g);

            if (chineseCharMatchRes != null) {
                let tipDomStr = "";
                chineseCharMatchRes = Array.from(new Set(chineseCharMatchRes))
                tipDomStr += "含有中文字符:<br>" + chineseCharMatchRes.join(" ") + "<br>";
                let tipDom = document.createElement("span");
                tipDom.style = "color:red";
                tipDom.innerHTML = tipDomStr;
                //插入提示DOM
                let codeDom = studentCodeDomList[i];
                codeDom.parentNode.insertBefore(tipDom, codeDom);
            }
        }
        //筛选重做学生，把信息标红
        //根据提交时间大于某个值来筛选

        function filter_redo(redo_date){
            for(let i = 0; i < student_list.length;i++){
                let submit_date = student_list[i].submit_date;
                if(submit_date > redo_date){
                    student_list[i].info_dom.color="red";
                    student_list[i].show();
                }
                else{
                    student_list[i].info_dom.color="blue";
                    student_list[i].hidden();
                }

                /*
                let hidden_flag = true;
                let e =  student_list[i].info_dom;
                if(e.color == "red"){
                    hidden_flag = false;
                }
                while(true){
                    //console.log(e);
                    if(e == null){
                        break;
                    }
                    if(e.contains(student_font_arr[i+1])){
                        break;
                    }


                    if(typeof (e.tagName) == "undefined"){
                        let parent = document.createElement("span");
                        let child = e;
                        child.parentNode.replaceChild(parent,child);//  获取子元素原来的父元素并将新父元素代替子元素
                        parent.appendChild(child);//  在新父元素下添加原来的子元素
                        e = parent;
                    }

                    e.hidden = hidden_flag;
                    e = e.nextSibling;
                }
                */



            }
        }

        //前面加入一个输入框
        const inputTemplate = '<textarea cols="40" rows="5" id="pythonWebOJTestInput" placeholder="输入程序需要从标准输入流读取的数据"></textarea>' +
            '<button id="startPythonOJTestButton"  type="button">提交</button>' +
            '<button id="clearPythonOJTestButton"  type="button">清空</button>' +
            '<button id="redoFilterPythonOJTestButton"  type="button">重做</button>';
        //第0个不一定是案例，直接加在题目旁边
        var firstDivDom = document.getElementsByClassName("autoBR")[0];
        var inputDimDom = document.createElement('div');
        inputDimDom.style = "float:right";
        firstDivDom.parentNode.insertBefore(inputDimDom, firstDivDom);
        inputDimDom.innerHTML = inputTemplate;
        //给按钮绑定个函数
        document.getElementById("startPythonOJTestButton").addEventListener('click', requestAnswer);
        document.getElementById("clearPythonOJTestButton").addEventListener('click', function () {
            students.clearAllAnswer();
        });

        document.getElementById("redoFilterPythonOJTestButton").addEventListener('click', function (){
            let redo_button_dom =  document.getElementById("redoFilterPythonOJTestButton");
            let min_date = null;
            let max_date = null;

            for (let i = 0; i < student_list.length; i++) {
                let submit_date = student_list[i].submit_date;
                if (min_date == null) {
                    min_date = submit_date;
                }
                if (max_date == null) {
                    max_date = submit_date;
                }
                if (min_date > submit_date) {
                    min_date = submit_date;
                }
                if (max_date < submit_date) {
                    max_date = submit_date;
                }

            }
            if(redo_button_dom.innerText == "重做") {
                if ((max_date - min_date) >= 7 * 24 * 60 * 60 * 1000) {
                    //差值大于一周说明有重做的
                    //let redo_date_str = prompt("输入重做时间(年-月-日):");
                    let redo_date = new Date(Date.parse(min_date));
                    redo_date.setDate(redo_date.getDate() + 7);
                    filter_redo(redo_date);
                    redo_button_dom.innerText = "显示全部";
                }

                //let redo_date_str = prompt("输入重做时间(年-月-日):");
                //filter_redo(new Date(redo_date_str));
            }
            else{
                let show_all_date = new Date(Date.parse(min_date));
                show_all_date.setDate(show_all_date.getDate() - 7);
                filter_redo(show_all_date);//用于显示之前隐藏的dom

                //下面是把颜色改回来
                for(let i = 0; i < student_list.length;i++){
                    student_list[i].info_dom.color = "blue";
                }
                redo_button_dom.innerText = "重做";
            }
        });

        // 通过评语来备份学生成绩
         function backupAllScore(){
               for(let i = 0; i < student_list.length;i++){
                   student_list[i].backupScore();
               }
         }

         function restoreAllScore(){
               for(let i = 0; i < student_list.length;i++){
                   student_list[i].restoreScore();
               }
         }
        unsafeWindow.restoreAllScore = restoreAllScore;

        function myEnhancedSave() {
            //写缓存
            //先获取问题,以问题作为key值
            let question = document.getElementsByClassName("autoBR")[0].innerText;
            let value = {};
            //滚动条位置
            value["scrollTop"] = document.documentElement.scrollTop;
            //input值
            let input = document.getElementById("pythonWebOJTestInput").value;
            //程序运行值
            value["input"] = input;
            //答案列表
            let answerList = [];
            for (let i = 0; i < students.length; i++) {
                answerList.push(students.getAnswer(i));
            }
            value["answerList"] = answerList;
            sessionStorage.setItem(question, JSON.stringify(value));
            // 作业分数备份，用于系统自动变动分数的还原
            backupAllScore();
            //最后触发原先的保存功能
            let oldSaveButton = document.getElementById("submit1");
            //  兼容IE
            if (document.all) {
                oldSaveButton.click();
            }
            //  兼容其它浏览器
            else {
                var e = document.createEvent("MouseEvents");
                e.initEvent("click", true, true);
                oldSaveButton.dispatchEvent(e);
            }
        }

        //自己写个保存按钮
        var submit1Dom = document.getElementById("submit1");
        var fixedSubmitButtonDom = submit1Dom.cloneNode(true);
        fixedSubmitButtonDom.id = "myFixedSubmitButton";
        fixedSubmitButtonDom.style = "position:fixed;top:5%;right:5%";
        submit1Dom.parentNode.insertBefore(fixedSubmitButtonDom, submit1Dom);
        //绑定一个函数
        fixedSubmitButtonDom.addEventListener('click', myEnhancedSave);

        //备份按钮
        var fixedBackScoreDom = submit1Dom.cloneNode(true);
        fixedBackScoreDom.id = "myFixedBackScoreButton";
        fixedBackScoreDom.style = "position:fixed;top:10%;right:5%";
        fixedBackScoreDom.value = "备份";
        fixedBackScoreDom.type = "button";
        submit1Dom.parentNode.insertBefore(fixedBackScoreDom, submit1Dom);
        //绑定一个函数
        fixedBackScoreDom.addEventListener('click', backupAllScore);

        //还原按钮
        var fixedRestoreScoreDom = submit1Dom.cloneNode(true);
        fixedRestoreScoreDom.id = "myFixedRestoreScoreButton";
        fixedRestoreScoreDom.style = "position:fixed;top:15%;right:5%";
        fixedRestoreScoreDom.value = "还原";
        fixedRestoreScoreDom.type = "button";
        submit1Dom.parentNode.insertBefore(fixedRestoreScoreDom, submit1Dom);
        //绑定一个函数
        fixedRestoreScoreDom.addEventListener('click', restoreAllScore);

        //如果有缓存的话读取缓存
        function readCache() {
            let question = document.getElementsByClassName("autoBR")[0].innerText;
            let value = sessionStorage.getItem(question);
            if (value != null) {
                value = JSON.parse(value);
                let answerList = value["answerList"];
                //数目相同才从缓存内读取并显示,主要是只显示需要批改的作业导致数目变化
                if (answerList.length == students.length) {
                    document.getElementById("pythonWebOJTestInput").value = value["input"];
                    for (let i = 0; i < students.length; i++) {
                        students.setAnswer(i, answerList[i]);
                    }
                    document.documentElement.scrollTop = value["scrollTop"];
                }
            }
        }

        readCache();
        //把保存按钮浮动到右上
        //document.getElementById("submit1").style="position:fixed;top:5%;right:5%"
    }

    if(homework_summary_reg.test(window.location.href)){
        //作业汇总导出表代码
        console.log("作业汇总增强");

         function requestDownloadAll() {
            GM_xmlhttpRequest({
                method: "post",
                url: "http://localhost:8000/download/all",
                responseType:"blob",
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                data: JSON.stringify({
                    "document": originalPageHTML
                }),
                onload: function (response) {
                    let blob = response.response;
                    let fileName_reg = /filename\*=utf-8''(.*)/;
                    let fileName = response.responseHeaders.match(fileName_reg)[1];
                    fileName = decodeURI(fileName);

                    let downloadElement = document.createElement('a');
                    let href = window.URL.createObjectURL(blob); // 创建下载的链接
                    downloadElement.href = href;
                    downloadElement.download = fileName; // 下载后文件名
                    document.body.appendChild(downloadElement);
                    downloadElement.click(); // 点击下载
                    document.body.removeChild(downloadElement); // 下载完成移除元素
                    window.URL.revokeObjectURL(href); // 释放掉blob对象
                },
                onerror: function (response) {
                    console.log("请求失败");
                }
            });
        }


         function requestDownloadRedo() {
            GM_xmlhttpRequest({
                method: "post",
                url: "http://localhost:8000/download/redo",
                responseType:"blob",
                headers: {
                    "Content-Type": "application/json;charset=utf-8"
                },
                data: JSON.stringify({
                    "document": originalPageHTML
                }),
                onload: function (response) {
                    let blob = response.response;
                    let fileName_reg = /filename\*=utf-8''(.*)/;
                    let fileName = response.responseHeaders.match(fileName_reg)[1];
                    fileName = decodeURI(fileName);

                    let downloadElement = document.createElement('a');
                    let href = window.URL.createObjectURL(blob); // 创建下载的链接
                    downloadElement.href = href;
                    downloadElement.download = fileName; // 下载后文件名
                    document.body.appendChild(downloadElement);
                    downloadElement.click(); // 点击下载
                    document.body.removeChild(downloadElement); // 下载完成移除元素
                    window.URL.revokeObjectURL(href); // 释放掉blob对象
                },
                onerror: function (response) {
                    console.log("请求失败");
                }
            });
        }

        var download_all_btn = document.createElement("button");
        download_all_btn.id = "download_all";
        download_all_btn.style = "margin-right:10px";
        download_all_btn.innerText = "导出所有";
        download_all_btn.type = "button";
        download_all_btn.addEventListener('click', requestDownloadAll);

        var download_redo_btn = document.createElement("button");
        download_redo_btn.id = "download_redo";
        download_redo_btn.style = "margin-right:10px";
        download_redo_btn.innerText = "导出重做";
        download_redo_btn.type = "button";
        download_redo_btn.addEventListener('click', requestDownloadRedo);
        var firstSummaryDom = document.getElementById("MainContent_btnExam");
        firstSummaryDom.parentNode.insertBefore(download_all_btn,firstSummaryDom);
        firstSummaryDom.parentNode.insertBefore(download_redo_btn,firstSummaryDom);


    }

    if(single_student_homework_page_reg.test(window.location.href)){
        console.log("学生作业详情页——显示试卷");
        //把补交答案丢到右上角固定
        var submit_answer_btn_dom = document.getElementById("Button1");
        submit_answer_btn_dom.style = "position:fixed;top:5%;right:5%";
        // 找填写补交答案的dom
        var table_dom_arr = document.getElementsByTagName("table");
        var submit_student_answer_dom = null;
        for(let i = table_dom_arr.length - 1; i >= 0 ; i--){
            let table_dom = table_dom_arr[i];
            var keys = ["补交学生答案", "题号", "学生答案"];
            let j = 0;
            for(; j < keys.length; j++){
                let key = keys[j];
                if(table_dom.innerText.indexOf(key)==-1){
                    break;
                }
            }
            if (j ==keys.length ){
                submit_student_answer_dom = table_dom;
                break;
            }
        }
        if (submit_student_answer_dom){
            //如果有的话就固定到右上角
            submit_student_answer_dom.style = "position:fixed;top:10%;right:5%";
        }
    }
    // Your code here...
})();