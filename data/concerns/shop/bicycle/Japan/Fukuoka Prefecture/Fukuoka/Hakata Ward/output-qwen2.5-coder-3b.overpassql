[out:json][timeout:30];
area["name:en"="Hakata Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
