[out:json][timeout:30];
area["name:en"="Higashiyodogawa Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
