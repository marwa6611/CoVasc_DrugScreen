$fn=100;
module oval(w,h, height, center = false) {
 scale([1, h/w, 1]) cylinder(h=height, r=w, center=center);
}

module insert(depth=7.5, diameter=6, embryodiameter=0.7,sphere_d=0.35,raise=4.)   
{
    
    translate([0,0,-depth-raise]) hull(){
        rotate([90, 0, 90]) cylinder(h=diameter/1.5,d=embryodiameter,center=true);
        translate([0,0,depth]) oval(w=diameter/2,h=diameter/2.5,height=raise);
    }
    //rotate([90, 0, 0]) cylinder(h=diameter/3,d=embryodiameter,center=true);
    //translate([0,0.3,-raise-depth/2]) scale([0.4, 0.75, 0.5]) sphere(sphere_d);
    translate([-0.65,0,-depth-raise-0.3]) scale([1.0, 0.9, 1.0]) sphere(sphere_d);
    
    
    //translate([0,shift-(3),-depth+(sphere_h)]) sphere(sphere_d);
    
    //translate([sphere_shift-(0.2),shift-(4.5),-depth+(sphere_h)]) sphere(sphere_d+(0.4));
    
    //translate([sphere_shift,shift,-depth]) sphere(sphere_d+1);
    
    
    
}

module platform(x_pos=-62.5,y_pos=-37.5){
   
//translate([x_pos,y_pos,-5]) cylinder(h=10,d=5,center=false);
//translate([x_pos,y_pos,-5]) cylinder(h=10,d=5,center=false);
translate([x_pos+2.5,y_pos+2.5,0]) cube([112.5,75,2],0);
//translate([-2.5,-2.5,2]) cube([5,5,10], 0);
//translate([x_pos,y_pos,-10]) cylinder(h=10,r=190,center=false);
xdistance=9;
ydistance=9;
    
for (x = [1:12], y = [1:8])
        translate([x_pos+(xdistance*x),y_pos+(ydistance *y)]) insert();

}

platform();