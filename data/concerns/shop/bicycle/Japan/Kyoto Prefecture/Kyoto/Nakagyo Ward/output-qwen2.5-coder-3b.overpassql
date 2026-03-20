[out:json][timeout:30];
area["name:en"="Nakagyo Ward"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
