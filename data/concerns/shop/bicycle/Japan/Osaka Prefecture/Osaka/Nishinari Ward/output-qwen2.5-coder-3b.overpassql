[out:json][timeout:30];
area["name:en"="Nishinari Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
