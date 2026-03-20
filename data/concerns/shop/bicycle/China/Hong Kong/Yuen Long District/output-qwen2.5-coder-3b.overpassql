[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
