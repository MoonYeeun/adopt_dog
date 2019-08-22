SELECT * FROM adopt_dog2.shelter_list;
SET @CNT=0;
UPDATE shelter_list SET shelter_list.index=@CNT:=@CNT+1;