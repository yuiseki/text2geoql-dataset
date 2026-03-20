[out:json][timeout:30];
area["name:en"="Sai Kung District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
