[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["shop"~"department_store"](area.outer);
);
out geom;
