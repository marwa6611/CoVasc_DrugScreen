path="E:/Data_Drug_Screening_CovidBox/Acquifer/20210312_7th_session/20210318_drug_screen_FliV_Myl7mR_2H02_2H11/Measurements/";
file="2H02-2H11_Summary_measurements";

directory=getDirectory("Choose the directory");


//well=getString("Type in the well eg. A001", "A001");
//print(directory, well);

newDirectory=replace(directory, "\\", "/");
listDir=getFileList(newDirectory);
print(listDir[0]);

run("Set Measurements...", "area perimeter shape area_fraction display redirect=None decimal=3");
letterWell=newArray("A","B","C","D","E","F","G","H");
//letterWell=newArray("F","G","H");
numberWell=newArray("001","002","003","004","005","006","007","008","009","010","011","012");

setBatchMode("show");
for (i = 0; i < lengthOf(letterWell); i++) {
letter=letterWell[i];

for (j = 0; j < lengthOf(numberWell); j++) {
run("Clear Results");

	
well=letter + numberWell[j];
//if(well=="B001" || well=="B002"|| well=="B003" || well=="B004" || well=="B005" || well=="B006"|| well=="B007" ){
//continue
//} 
run("Image Sequence...", "open="+ newDirectory + "" +listDir[0]+" number=11 file="+ well +"--PO01--LO001--CO3 sort use");
setMinAndMax(537, 1000);

title=getTitle();

if(i==0 && j==0){
makeLine(462, 975, 1659, 954);
}
else {
makeLine(x1, y1, x2, y2);
}

waitForUser("Line okay?");

getSelectionCoordinates(xpoints, ypoints);
x1=xpoints[0];
x2=xpoints[1];
y1=ypoints[0];
y2=ypoints[1];


//setTool("multipoint");
//run("Enhance Contrast", "saturated=0.65");
//run("Subtract Background...", "rolling=50 stack");




selectWindow(title);



run("Multi Kymograph", "linewidth=1");

selectWindow("Kymograph");
run("Gaussian Blur...", "sigma=2");
run("Find Maxima...", "prominence=15 output=[Point Selection]");
run("Set Measurements...", "centroid display redirect=None decimal=3");
run("Measure");
test_count=nResults();
realTitle=getResultLabel(0);
run("Clear Results");
waitForUser("The count is "+test_count+", maxima okay?");


run("Measure");


ISV_count=nResults();









close("*");



run("Image Sequence...", "open="+ newDirectory + "" +listDir[0]+" number=11 file="+ well +"--PO01--LO001--CO6 sort use");

Dialog.createNonBlocking("Evaluation");
Dialog.addChoice("Edema", newArray("Yes","No"),"No");
Dialog.addChoice("Heart beat", newArray("Yes","No"),"Yes");
Dialog.show();
edema=Dialog.getChoice();
heartbeat=Dialog.getChoice();

run("Clear Results");
run("Select None");
makeLine(x1, y1, x2, y2);
setTool("line");
waitForUser("measure size");
run("Measure");
realTitle=getResultLabel(0);
length_measure=getResult("Length", 0);

run("Select None","");

//save("D:/Downloads/20201119_2nd_session/201119_drugscreen_A02_A11_FliV_BF/export/"+ well +".tif");

if (File.exists(path  + file + ".csv")) 
{
File.append(realTitle + ","+ ISV_count + ","+ edema + ","+ heartbeat+","+length_measure, path + file + ".csv");
}

else{
File.open(path + file +".csv"); 
File.append("Image_title,N_ISV,Edema,Hearbeat,Length,\n"+ realTitle + ","+ ISV_count + ","+ edema + ","+ heartbeat+","+ length_measure, path + file + ".csv");



close();
}
close("*");
run("Clear Results");
run("Collect Garbage");
}
}
setBatchMode("show");
close("*");

path="E:/Data_Drug_Screening_CovidBox/Acquifer/20210312_7th_session/20210318_drug_screen_FliV_Myl7mR_2G02_2G11/Measurements/";
file="2G02-2G11_Summary_measurements";
File.close(path+file+".csv"); 

directory=getDirectory("Choose the directory");
//well=getString("Type in the well eg. A001", "A001");
//print(directory, well);

newDirectory=replace(directory, "\\", "/");
listDir=getFileList(newDirectory);
print(listDir[0]);

run("Set Measurements...", "area shape area_fraction display redirect=None decimal=3");
letterWell=newArray("A","B","C","D","E","F","G","H");
//letterWell=newArray("F","G","H");
numberWell=newArray("001","002","003","004","005","006","007","008","009","010","011","012");

setBatchMode("show");
for (i = 0; i < lengthOf(letterWell); i++) {
letter=letterWell[i];

for (j = 0; j < lengthOf(numberWell); j++) {


	
well=letter + numberWell[j];
run("Image Sequence...", "open="+ newDirectory + "" +listDir[0]+" number=100 file="+ well +"--PO01--LO001--CO5 sort use");

title=getTitle();
label=getInfo("slice.label");

getStatistics(area, mean, min, max, std, histogram);
if(std<22)
{
run("Image Sequence...", "open="+ newDirectory + "" +listDir[0]+" number=100 file="+ well +"--PO01--LO001--CO6 sort use");
run("8-bit");
run("Stack Difference", "gap=1");
selectWindow("Difference Image");
rename("Difference_Image");
run("Gaussian Blur...", "sigma=3 stack");
run("Z Project...", "projection=[Max Intensity]");
selectWindow("MAX_Difference_Image");
run("Gaussian Blur...", "sigma=3");
run("Auto Threshold", "method=Intermodes white");
roiManager("reset");
run("Create Selection");
roiManager("Add");
run("Enlarge...", "enlarge=-30");
run("Select Bounding Box");
roiManager("Add");
Roi.getCoordinates(xpoints, ypoints);

Array.print(xpoints);
Array.print(ypoints);
Xavg=(xpoints[0]+xpoints[1])/2;
ybord_low=ypoints[2]+15 ;
ybord_high=ypoints[2]-15 ;


makeLine(Xavg, ybord_high, Xavg, ybord_low, 1);
roiManager("Add");
selectWindow("Difference_Image");
roiManager("Select", 2);
waitForUser("Line okay?");

run("Multi Kymograph", "linewidth=1");

selectWindow("Kymograph");
run("Gaussian Blur...", "sigma=2 stack");
run("Find Maxima...", "prominence=90 output=[Point Selection]");
waitForUser("Maxima okay?");
run("Set Measurements...", "centroid display redirect=None decimal=3");
run("Measure");
result_count=nResults();

selectWindow("Kymograph");
close();
close("*");	
}


else{
roiManager("reset");
run("Duplicate...", "duplicate title=Segmentation");
selectWindow("Segmentation");
run("Gaussian Blur...", "sigma=5 stack");
run("Subtract Background...", "rolling=50 stack");
run("Auto Threshold", "method=Default white");
run("Create Selection");
roiManager("Add");
run("Enlarge...", "enlarge=-30");
run("Select Bounding Box");
roiManager("Add");
Roi.getCoordinates(xpoints, ypoints);

Array.print(xpoints);
Array.print(ypoints);
Xavg=(xpoints[0]+xpoints[1])/2;
ybord_low=ypoints[2]+15 ;
ybord_high=ypoints[2]-15 ;


makeLine(Xavg, ybord_high, Xavg, ybord_low, 1);
roiManager("Add");


selectWindow(title);
roiManager("Select", 2);
waitForUser("Line okay?");
run("Multi Kymograph", "linewidth=1");

selectWindow("Kymograph");
run("Find Maxima...", "prominence=90 output=[Point Selection]");
waitForUser("Maxima okay?");

run("Set Measurements...", "centroid display redirect=None decimal=3");
run("Measure");
result_count=nResults();



selectWindow("Kymograph");
close();
}
close("*");
//save("D:/Downloads/20201119_2nd_session/201119_drugscreen_A02_A11_FliV_BF/export/"+ well +".tif");
path="E:/Data_Drug_Screening_CovidBox/Acquifer/20210312_7th_session/20210318_drug_screen_FliV_Myl7mR_2H02_2H11/Measurements/";
file="2H02-2H11_Summary_heartbeat";
if (File.exists(path  + file + ".csv")) 
{
File.append(title+"," + label + ","+ result_count +","+ "100" , path + file + ".csv");
}

else{
File.open(path + file +".csv"); 
File.append("Image_title,Label,Hearbeat,Slices\n"+ title+"," + label + ","+ result_count +","+ 100, path + file + ".csv");




}
run("Clear Results");
run("Collect Garbage");
}
}
setBatchMode("show");
