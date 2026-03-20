[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
