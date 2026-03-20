[out:json][timeout:30];
area["name:en"="Niigata"][boundary=administrative]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["shop"="bakery"](area.inner)(area.outer);
);
out geom;
