[out:json][timeout:30];
area["name:en"="Kita Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
