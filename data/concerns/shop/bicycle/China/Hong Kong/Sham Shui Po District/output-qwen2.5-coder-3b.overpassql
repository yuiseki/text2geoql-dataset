[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
