[out:json][timeout:30];
area["name:en"="Islands District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
