[out:json][timeout:30];
area["name:en"="Nagoya"][boundary=administrative]->.outer;
area["name:en"="Aichi Prefecture"]->.inner;
(
  nwr["shop"="bakery"](area.inner)(area.outer);
);
out geom;
