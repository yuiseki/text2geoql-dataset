[out:json][timeout:30];
area["name:en"="Higashinari Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
