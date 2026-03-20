[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["shop"~"bicycle"](area.inner)(area.outer);
);
out geom;
