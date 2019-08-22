USE adopt_dog;
SELECT * FROM dog_list;
SET @CNT=0;
UPDATE dog_list SET dog_list.index=@CNT:=@CNT+1;

SELECT * FROM dog_list;

