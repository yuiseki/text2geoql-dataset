[out:json][timeout:30];
area["name:en"="North District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
