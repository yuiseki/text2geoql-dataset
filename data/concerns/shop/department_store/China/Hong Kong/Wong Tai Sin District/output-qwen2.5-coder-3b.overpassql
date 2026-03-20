[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["shop"~"department_store"](area.outer);
);
out geom;
