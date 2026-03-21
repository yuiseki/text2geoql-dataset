[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["historic"~"ruins"](area.inner)(area.outer);
);
out geom;
