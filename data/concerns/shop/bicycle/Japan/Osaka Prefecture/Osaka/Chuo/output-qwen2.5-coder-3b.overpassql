[out:json][timeout:30];
area["name:en"="Chuo"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
