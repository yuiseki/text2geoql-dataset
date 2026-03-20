[out:json][timeout:30];
area["name:en"="Yodogawa Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
