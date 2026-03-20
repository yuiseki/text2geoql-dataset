[out:json][timeout:30];
area["name:en"="Nishi Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
