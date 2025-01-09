# Exam difficulty balancing

When thinking about the difficulty of an exam it is important to consider a few things:

1. Exams are only worth 50% of the course grade, with the expectation that students get the full 50% for homework.
    - This means getting a 40 on all the exams translates to a C, 60 to a B, and 80 to an A.
2. It is always easier to refactor an exercise to make it easier than to make it more difficult.

## Point values

Exercises are assigned point values based on their relative difficulty (number of concepts, number of steps, logic complexity, inputs/output complexity, code volume). One point is for easy exercises, three points is for hard exercises, and two points is in-between.  

### Balancing

|Points|Min|Max|
|:---|---:|---:|
|1-pt|2|3|
|2-pt|3|5|
|3-pt|1|2|

### Free Exercise

One "free" exercise worth 1 point is permitted. This is done to raise the floor of possible scores. 

### Making exercises easier

It will usually be the case that an exercise needs to be made easier to fit into the exam. These strategies are effective:

- Improve the prompt (better example, explain different way, graphics, etc)
- Provide a hint on tricky bits which may be overlooked
- Nudge the student by providing high-level steps in order
- Provide some of the solution as startercode

## Points Cap

Exams are scored with a points cap. I.E. `score = min((1, points/points_cap))`.

- Completing all 1 point exercises should score at least 20% of the cap.
- Completing all 1 and 2 point exercises should score of roughly 80% of the cap.
- Students should be required to solve at least one 3 point exercise to score 100% of the cap.

## Time Limit

Generally 3.5-4 hours is the time limit. In past iterations of the course that has been consistent with median TA testers completing the entire exam in 1.5-2 hours. 
