
# Project II

## Table of contents

- [Deliverables](#deliverables)
- [Instructions](#instructions)
- [Evaluation](#evaluation)
- [Credits](#credits)

---

## Deliverables

You are requested to deliver a *tar.gz* archive containing:
 - Your report named `report.pdf`.
	 - Your report must be at most **5** pages long.
	 - Fill in the following [template](./template-project2.tex) to write your report.
	 - In French or English.
 - A file named `bayesfilter.py` containing your implementation of the Bayes filter algorithm.
     - Simply modify the provided `bayesfilter.py` file.
	 - :warning: Do not change the class name (`BeliefStateAgent`).
 - (optional) A file named `pacmanagent.py` containing your implementation of the BONUS.
     - Simply modify the provided `pacmanagent.py` file.

:warning: A penalty of **-2 points** on the final grade will be applied if the files are not named based on the instructions above.

---
## Instructions

This part is due by **September 20, 2025 at 23:59**. This is a **hard** deadline.

In this third part of the project, Pacman got tired of ghosts wandering around him. So he decided to buy a laser gun and kill them. But while he shot them, he figured out that the gun has instead turned them into invisible but edible ghosts! Fortunately, as it was part of a box that he bought from a flea market, he also got his hands on a rusty sensor, which still works but is subject to measurement errors which are described in the user manual.

A lot of confusion arose since Pacman shot the ghosts: he has no idea where they currently are in the maze! However, he knows that the ghosts are confused and should be willing to escape from him.
More precisely, he knows that the first ghost, named `scared`, is more fearful than the second ghost, named `afraid`, who is more fearful than the third ghost, named `confused`.

Your task is to design an intelligent agent based on the Bayes filter algorithm (see [Lecture 6](https://glouppe.github.io/info8006-introduction-to-ai/?p=lecture6.md)) for locating all the ghosts in the maze.

You may use the following command line to start a game where the sole eadible `scared` ghost wanders around the maze while Pacman, controlled by the `humanagent.py` policy, tries to locate him with a (very) rusty sensor:
```bash
python run.py --agentfile humanagent.py --bsagentfile bayesfilter.py --ghostagent scared --nghosts 1 --seed -1 --layout large_filter
```
Note that when you use multiple ghosts, they all run the same policy (e.g., all `scared`). Change the value of `seed` - for random number generator - to a positive value to ease reproducibility of your experiments.

You are asked to answer the following questions:

 1. **Bayes filter**
	 - 1.a. - **2 point** - Describe mathematically the sensor model of the rusty sensor, as implemented in `_get_evidence` of the `BeliefStateAgent` class.
	 - 1.b. - **2 points** - Provide a unified parametrized transition model from which the ghosts `scared`, `afraid` and `confused` can be derived. Derive this model from the ghost implementations found in `/pacman_module/ghostAgents.py` (functions `getDistribution`). Your model should specify a single free parameter.
     
     :warning: Be aware that in project 2, the ghosts are now able to go move backward, on the contrary to project 1.

    Answers to the previous questions should not make any reference to the API nor include pseudo-code.

 2. **Implementation**

 	- 2.a. - **6 points** - Implement the **Bayes filter** algorithm to compute Pacman's belief state. This should be done in the `_get_updated_belief` function of `bayesfilter.py`.
         - Your function `_get_updated_belief` (**2 points**) should use the functions `_get_sensor_model` (**2 points**) and `_get_transition_model` (**2 points**) that you should also define yourself.
 		 - Your implementation must work with multiple ghosts (all running the same policy).
 		 - Pacman's belief state should eventually converge to an uncertainty area for each ghost.
 		 - Your filter should consider the Pacman position, as Pacman may wander freely in the maze.

 3. **Experiment**

 	- 3.a. - **1 point** - Provide a measure which summarizes Pacman's belief state (i.e., its uncertainty).
 	- 3.b. - **1 point** - Provide a measure of the quality of the belief state(s). You may assume access to the ground truth (i.e., the true position of the ghost(s)).
 	- 3.c. - **3 points** - Run your filter implementation on the `/pacman_module/layouts/large_filter.lay` and the `/pacman_module/layouts/large_filter_walls.lay` layouts, against each type of ghost. Report your results graphically.
 		 - Record your measures (see `_record_metrics` function in `bayesfilter.py`) averaged over several trials.
 		 - Your results should come with error bars.
 		 - The number of trials must be high enough and their duration long enough so that the measures have converged.
 	- 3.d. - **1 points** - Discuss the effect of the ghost transition model parameter on its own behavior and on Pacman's belief state. Consider the two provided layouts. Motivate your answer by using your measures and the model itself. Use the default sensor variance.
 	- 3.e. - **1 points** - Discuss the effect of the sensor variance (as set through the `--sensorvariance` command line argument) on Pacman's belief state.
 	- 3.f. - **1 points** - How would you implement a Pacman controller to eat ghosts using only its current position, the set of legal actions and its current belief state?
 	- 3.g. - **BONUS 3 points** - Implement this controller in the `pacmanagent.py` file.

---

## Evaluation

Besides the questions you're expected to answer, you will also be evaluated according to the following criteria:

 - **Code style** - **2 points**
	 - **PEP8 compatibility** - **0.8 point** - PEP8 guidelines are provided at [Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/). A script will be executed to check the compatibility of your code.
		 - 0.8 point : the script runs without error.
		 - 0 point: any error during the execution of the script.
	 - **Specification** - **1.2 point** - correctness of the specification of your functions.
		- 1.2 point : all specifications are correct.
		- 0.9 point : at least 75% correct specifications.
		- 0.6 point : at least 50% correct specifications.
		- 0.3 point : at least 25% correct specifications.
		- 0 point : less than 25% correct specifications.

Note that your implementation might be tested on other layouts, with Pacman moving arbitrarily.

:warning: Take care of providing a clearly written report, which fully follows the provided template. We reserve the right to refuse to evaluate a report (i.e. to consider it as not provided) which would be difficult to read and understand. We may also refuse to evaluate discussion blocks that are truly confusing, even if the underlying idea might be right. Sanctions will be imposed in case of non-respect of the guidelines about the structure and length of the report:

 - Any modification of the template: **- 2 points**
 - Only the first 5 pages of the report will be taken into account for the evaluation.

:warning: Plagiarism is checked and sanctioned by a grade of 0. Cases of plagiarism will all be reported to the Faculty.

---

## Credits

The programming projects are adapted from [CS188 (UC Berkeley)](http://ai.berkeley.edu/project_overview.html).

---

# โปรเจกต์ 2 (ภาษาไทย)

## สารบัญ

- [สิ่งที่ต้องส่งมอบ](#deliverables-th)
- [คำแนะนำ](#instructions-th)
- [การประเมินผล](#evaluation-th)
- [เครดิต](#credits-th)

---

## สิ่งที่ต้องส่งมอบ (Deliverables) <a name="deliverables-th"></a>

คุณต้องส่งไฟล์ archive แบบ *tar.gz* ที่ประกอบด้วย:
 - รายงานของคุณชื่อ `report.pdf`
	 - รายงานของคุณต้องมีความยาวไม่เกิน **5** หน้า
	 - กรอกข้อมูลใน เทมเพลต ต่อไปนี้เพื่อเขียนรายงานของคุณ
	 - เป็นภาษาฝรั่งเศสหรือภาษาอังกฤษ
 - ไฟล์ชื่อ `bayesfilter.py` ที่มีการนำอัลกอริทึม Bayes filter ไปใช้ของคุณ
     - เพียงแค่แก้ไขไฟล์ `bayesfilter.py` ที่ให้มา
	 - :warning: อย่าเปลี่ยนชื่อคลาส (`BeliefStateAgent`)
 - (ทางเลือก) ไฟล์ชื่อ `pacmanagent.py` ที่มีการนำโบนัสไปใช้ของคุณ
     - เพียงแค่แก้ไขไฟล์ `pacmanagent.py` ที่ให้มา

:warning: จะมีการหักคะแนน **-2 คะแนน** จากคะแนนสุดท้ายหากไฟล์ไม่ได้ตั้งชื่อตามคำแนะนำข้างต้น

---
## คำแนะนำ (Instructions) <a name="instructions-th"></a>

ส่วนนี้มีกำหนดส่งภายใน **20 กันยายน 2025 เวลา 23:59 น.** นี่คือ **กำหนดส่งที่ตายตัว**

ในส่วนที่สามของโปรเจกต์นี้ แพคแมนเบื่อผีที่เดินเตร่ไปรอบๆ ตัวเขา เขาจึงตัดสินใจซื้อปืนเลเซอร์และฆ่าพวกมัน แต่ในขณะที่เขายิงพวกมัน เขาก็พบว่าปืนกลับทำให้พวกมันกลายเป็นผีที่มองไม่เห็นแต่กินได้! โชคดีที่มันเป็นส่วนหนึ่งของกล่องที่เขาซื้อมาจากตลาดนัด เขายังได้เซ็นเซอร์ที่ขึ้นสนิมมาด้วย ซึ่งยังคงใช้งานได้แต่มีข้อผิดพลาดในการวัดซึ่งอธิบายไว้ในคู่มือผู้ใช้

ความสับสนมากมายเกิดขึ้นตั้งแต่แพคแมนยิงผี: เขาไม่รู้ว่าตอนนี้พวกมันอยู่ที่ไหนในเขาวงกต! อย่างไรก็ตาม เขารู้ว่าผีสับสนและน่าจะต้องการหนีจากเขา พูดให้ชัดเจนคือ เขารู้ว่าผีตัวแรกชื่อ `scared` ขี้กลัวกว่าผีตัวที่สองชื่อ `afraid` ซึ่งขี้กลัวกว่าผีตัวที่สามชื่อ `confused`

งานของคุณคือการออกแบบเอเจนต์อัจฉริยะโดยใช้อัลกอริทึม Bayes filter (ดู บรรยายที่ 6) เพื่อระบุตำแหน่งของผีทั้งหมดในเขาวงกต

คุณสามารถใช้บรรทัดคำสั่งต่อไปนี้เพื่อเริ่มเกมที่ผี `scared` ที่กินได้เพียงตัวเดียวเดินเตร่ไปรอบๆ เขาวงกต ในขณะที่แพคแมนซึ่งควบคุมโดยนโยบาย `humanagent.py` พยายามระบุตำแหน่งของมันด้วยเซ็นเซอร์ที่ขึ้นสนิม (มาก):
```bash
python run.py --agentfile humanagent.py --bsagentfile bayesfilter.py --ghostagent scared --nghosts 1 --seed -1 --layout large_filter
```
โปรดทราบว่าเมื่อคุณใช้ผีหลายตัว พวกมันทั้งหมดจะใช้นโยบายเดียวกัน (เช่น ทั้งหมดเป็น `scared`) เปลี่ยนค่า `seed` - สำหรับตัวสร้างเลขสุ่ม - เป็นค่าบวกเพื่อให้ง่ายต่อการทำซ้ำการทดลองของคุณ

คุณต้องตอบคำถามต่อไปนี้:

 1. **Bayes filter**
	 - 1.a. - **2 คะแนน** - อธิบายแบบจำลองเซ็นเซอร์ของเซ็นเซอร์ที่ขึ้นสนิมในทางคณิตศาสตร์ ตามที่นำไปใช้ใน `_get_evidence` ของคลาส `BeliefStateAgent`
	 - 1.b. - **2 คะแนน** - นำเสนอแบบจำลองการเปลี่ยนสถานะแบบมีพารามิเตอร์ที่เป็นหนึ่งเดียวซึ่งสามารถสืบทอดพฤติกรรมของผี `scared`, `afraid` และ `confused` ได้ สืบทอดแบบจำลองนี้จากการนำไปใช้ของผีที่พบใน `/pacman_module/ghostAgents.py` (ฟังก์ชัน `getDistribution`) แบบจำลองของคุณควรกำหนดพารามิเตอร์อิสระเพียงตัวเดียว
     
     :warning: โปรดทราบว่าในโปรเจกต์ 2 ผีสามารถเคลื่อนที่ถอยหลังได้แล้ว ซึ่งตรงข้ามกับโปรเจกต์ 1

    คำตอบของคำถามก่อนหน้านี้ไม่ควรมีการอ้างอิงถึง API หรือรวมโค้ดเทียม (pseudo-code)

 2. **การนำไปใช้ (Implementation)**

 	- 2.a. - **6 คะแนน** - นำอัลกอริทึม **Bayes filter** ไปใช้เพื่อคำนวณสถานะความเชื่อ (belief state) ของแพคแมน ซึ่งควรทำในฟังก์ชัน `_get_updated_belief` ของ `bayesfilter.py`
         - ฟังก์ชัน `_get_updated_belief` ของคุณ (**2 คะแนน**) ควรใช้ฟังก์ชัน `_get_sensor_model` (**2 คะแนน**) และ `_get_transition_model` (**2 คะแนน**) ที่คุณควรต้องนิยามเองด้วย
 		 - การนำไปใช้ของคุณต้องทำงานกับผีหลายตัวได้ (ทั้งหมดใช้นโยบายเดียวกัน)
 		 - สถานะความเชื่อของแพคแมนควรจะลู่เข้าสู่พื้นที่ที่ไม่แน่นอนสำหรับผีแต่ละตัวในที่สุด
 		 - ตัวกรองของคุณควรพิจารณาตำแหน่งของแพคแมน เนื่องจากแพคแมนอาจเดินเตร่ไปมาในเขาวงกตได้อย่างอิสระ

 3. **การทดลอง (Experiment)**

 	- 3.a. - **1 คะแนน** - นำเสนอตัวชี้วัดที่สรุปสถานะความเชื่อของแพคแมน (เช่น ความไม่แน่นอนของมัน)
 	- 3.b. - **1 คะแนน** - นำเสนอตัวชี้วัดคุณภาพของสถานะความเชื่อ คุณสามารถสมมติว่าสามารถเข้าถึงความจริงพื้นฐานได้ (เช่น ตำแหน่งที่แท้จริงของผี)
 	- 3.c. - **3 คะแนน** - รันการนำไปใช้ตัวกรองของคุณบนเลย์เอาต์ `/pacman_module/layouts/large_filter.lay` และ `/pacman_module/layouts/large_filter_walls.lay` กับผีแต่ละประเภท รายงานผลของคุณในรูปแบบกราฟิก
 		 - บันทึกตัวชี้วัดของคุณ (ดูฟังก์ชัน `_record_metrics` ใน `bayesfilter.py`) โดยเฉลี่ยจากการทดลองหลายครั้ง
 		 - ผลลัพธ์ของคุณควรมาพร้อมกับแถบข้อผิดพลาด (error bars)
 		 - จำนวนการทดลองต้องสูงพอและระยะเวลาต้องนานพอเพื่อให้ตัวชี้วัดลู่เข้า
 	- 3.d. - **1 คะแนน** - อภิปรายผลของพารามิเตอร์แบบจำลองการเปลี่ยนสถานะของผีต่อพฤติกรรมของมันเองและต่อสถานะความเชื่อของแพคแมน พิจารณาเลย์เอาต์ที่ให้มาสองแบบ ให้เหตุผลคำตอบของคุณโดยใช้ตัวชี้วัดและตัวแบบจำลองเอง ใช้ค่าความแปรปรวนของเซ็นเซอร์ที่เป็นค่าเริ่มต้น
 	- 3.e. - **1 คะแนน** - อภิปรายผลของความแปรปรวนของเซ็นเซอร์ (ตามที่ตั้งค่าผ่านอาร์กิวเมนต์บรรทัดคำสั่ง `--sensorvariance`) ต่อสถานะความเชื่อของแพคแมน
 	- 3.f. - **1 คะแนน** - คุณจะนำตัวควบคุมแพคแมนไปใช้เพื่อกินผีโดยใช้เพียงตำแหน่งปัจจุบัน, ชุดของการกระทำที่ถูกกฎหมาย และสถานะความเชื่อปัจจุบันของมันได้อย่างไร?
 	- 3.g. - **โบนัส 3 คะแนน** - นำตัวควบคุมนี้ไปใช้ในไฟล์ `pacmanagent.py`

---

## การประเมินผล (Evaluation) <a name="evaluation-th"></a>

นอกเหนือจากคำถามที่คุณต้องตอบแล้ว คุณจะถูกประเมินตามเกณฑ์ต่อไปนี้ด้วย:

 - **สไตล์ของโค้ด** - **2 คะแนน**
	 - **ความเข้ากันได้กับ PEP8** - **0.8 คะแนน** - แนวทาง PEP8 มีให้ที่ Style Guide for Python Code จะมีการรันสคริปต์เพื่อตรวจสอบความเข้ากันได้ของโค้ดของคุณ
		 - 0.8 คะแนน : สคริปต์ทำงานโดยไม่มีข้อผิดพลาด
		 - 0 คะแนน: มีข้อผิดพลาดใดๆ ระหว่างการรันสคริปต์
	 - **ข้อกำหนด (Specification)** - **1.2 คะแนน** - ความถูกต้องของข้อกำหนดของฟังก์ชันของคุณ
		- 1.2 คะแนน : ข้อกำหนดทั้งหมดถูกต้อง
		- 0.9 คะแนน : ข้อกำหนดถูกต้องอย่างน้อย 75%
		- 0.6 คะแนน : ข้อกำหนดถูกต้องอย่างน้อย 50%
		- 0.3 คะแนน : ข้อกำหนดถูกต้องอย่างน้อย 25%
		- 0 คะแนน : ข้อกำหนดถูกต้องน้อยกว่า 25%

โปรดทราบว่าการนำไปใช้ของคุณอาจถูกทดสอบบนเลย์เอาต์อื่นๆ โดยที่แพคแมนเคลื่อนที่อย่างสุ่ม

:warning: โปรดระมัดระวังในการจัดทำรายงานที่เขียนอย่างชัดเจน ซึ่งเป็นไปตามเทมเพลตที่ให้มาอย่างครบถ้วน เราขอสงวนสิทธิ์ในการปฏิเสธที่จะประเมินรายงาน (เช่น ถือว่าไม่ได้ส่ง) ซึ่งอ่านและเข้าใจได้ยาก เราอาจปฏิเสธที่จะประเมินส่วนอภิปรายที่สับสนอย่างแท้จริง แม้ว่าแนวคิดพื้นฐานอาจจะถูกต้องก็ตาม จะมีการลงโทษในกรณีที่ไม่ปฏิบัติตามแนวทางเกี่ยวกับโครงสร้างและความยาวของรายงาน:

 - การแก้ไขเทมเพลตใดๆ: **- 2 คะแนน**
 - จะพิจารณาเฉพาะ 5 หน้าแรกของรายงานในการประเมินผล

:warning: การคัดลอกผลงานจะถูกตรวจสอบและลงโทษด้วยคะแนน 0 กรณีการคัดลอกผลงานทั้งหมดจะถูกรายงานต่อคณะ

---

## เครดิต (Credits) <a name="credits-th"></a>

โปรเจกต์การเขียนโปรแกรมนี้ดัดแปลงมาจาก CS188 (UC Berkeley).
