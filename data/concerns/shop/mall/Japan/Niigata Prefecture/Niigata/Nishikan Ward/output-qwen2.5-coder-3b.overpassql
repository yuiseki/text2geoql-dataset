[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
