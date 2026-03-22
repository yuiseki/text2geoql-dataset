[out:json][timeout:30];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;