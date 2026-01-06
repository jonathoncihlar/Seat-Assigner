# Seat Assigner
This quick and dirty Python script assigns students to seats based on their requests. The algorithm randomly
selects a student and attempts to give them their first choice seat. If that seat has already been assigned, then the algorithm will attempt to assign a seat in descending order of the request. If no seat can be assigned, then the student is placed in a holding queue until all other students have been assigned seats, at which point students in the holding queue will be assigned a random available seat.

## Usage
`python3 assign_seats.py <seat_file> <request_file>`

## Seat File
The seat file is a simple text file that defines seat names with one unique seat per line. Seats
should be defined as integers.

### Example
```
1
2
3
4
5
10
32
```

## Request File
The request file is a simple text file that establishes student requests. The format is one student record
per line with the student's name first followed by a comma-separated list of their preferred seats.

### Example
```
John,1,3,2,10,11,12,13,14,15,16
Monica,3,2,1,22,23,21
Beto,1,2,3,4,5,6,7,8,9,10
```
