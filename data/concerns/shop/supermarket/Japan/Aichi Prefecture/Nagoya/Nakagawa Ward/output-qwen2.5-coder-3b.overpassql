[out:json][timeout:30];
area["name:en"="Japan"][boundary=administrative]->.outer;
area["name:en"="Aichi Prefecture"]->.inner;
(
  nwr["shop"~"supermarket"](area.inner)(area.outer);
);
out geom;
