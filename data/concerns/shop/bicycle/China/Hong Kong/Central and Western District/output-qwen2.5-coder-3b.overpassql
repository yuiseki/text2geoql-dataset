[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
