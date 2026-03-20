[out:json][timeout:30];
area["name:en"="Niigata"][boundary=administrative]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["shop"="supermarket"](area.inner)(area.outer);
);
out geom;
