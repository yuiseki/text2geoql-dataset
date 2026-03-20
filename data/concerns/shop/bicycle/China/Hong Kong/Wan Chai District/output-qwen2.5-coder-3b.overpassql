[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
