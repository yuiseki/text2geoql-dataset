[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
