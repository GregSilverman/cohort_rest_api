SELECT anon_1.patient_sid AS anon_1_patient_sid, anon_1.lft AS anon_1_lft, anon_1.rgt AS anon_1_rgt
FROM 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data 
WHERE clinical_data.string_value = %s) AS anon_2 
ON clinical_data.lft >= anon_2.lft AND clinical_data.rgt <= anon_2.rgt AND clinical_data.patient_sid = anon_2.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_1 INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data 
WHERE clinical_data.string_value = %s) AS anon_4 
ON clinical_data.lft >= anon_4.lft AND clinical_data.rgt <= anon_4.rgt AND clinical_data.patient_sid = anon_4.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_3 
ON anon_1.patient_sid = anon_3.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt
FROM clinical_data 
WHERE clinical_data.string_value = %s) AS anon_4 
ON clinical_data.lft >= anon_4.lft AND clinical_data.rgt <= anon_4.rgt AND clinical_data.patient_sid = anon_4.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_3 
ON anon_1.patient_sid = anon_5.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data 
WHERE clinical_data.string_value = %s) AS anon_4 
ON clinical_data.lft >= anon_4.lft AND clinical_data.rgt <= anon_4.rgt AND clinical_data.patient_sid = anon_4.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_3 
ON anon_1.patient_sid = anon_6.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data WHERE clinical_data.string_value = %s) AS anon_7 
ON clinical_data.lft >= anon_7.lft AND clinical_data.rgt <= anon_7.rgt AND clinical_data.patient_sid = anon_7.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_5 
ON anon_1.patient_sid = anon_3.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data WHERE clinical_data.string_value = %s) AS anon_7 
ON clinical_data.lft >= anon_7.lft AND clinical_data.rgt <= anon_7.rgt AND clinical_data.patient_sid = anon_7.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_5 
ON anon_1.patient_sid = anon_5.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data WHERE clinical_data.string_value = %s) AS anon_7 
ON clinical_data.lft >= anon_7.lft AND clinical_data.rgt <= anon_7.rgt AND clinical_data.patient_sid = anon_7.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_5 
ON anon_1.patient_sid = anon.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data 
WHERE clinical_data.string_value = %s) AS anon_8 
ON clinical_data.lft >= anon_8.lft AND clinical_data.rgt <= anon_8.rgt AND clinical_data.patient_sid = anon_8.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_6 
ON anon_1.patient_sid = anon_3.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data 
WHERE clinical_data.string_value = %s) AS anon_8 
ON clinical_data.lft >= anon_8.lft AND clinical_data.rgt <= anon_8.rgt AND clinical_data.patient_sid = anon_8.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_6 
ON anon_1.patient_sid = anon_5.patient_sid INNER JOIN 

(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data INNER JOIN attribute ON attribute.id = clinical_data.attribute_id INNER JOIN 
(SELECT clinical_data.patient_sid AS patient_sid, clinical_data.lft AS lft, clinical_data.rgt AS rgt 
FROM clinical_data \nWHERE clinical_data.string_value = %s) AS anon_8 
ON clinical_data.lft >= anon_8.lft AND clinical_data.rgt <= anon_8.rgt AND clinical_data.patient_sid = anon_8.patient_sid 
WHERE (attribute.attribute_value = %s) AND ((clinical_data.double_value = %s) OR (clinical_data.string_value = %s)) 
GROUP BY clinical_data.patient_sid) AS anon_6 
ON anon_1.patient_sid = anon_6.patient_sid