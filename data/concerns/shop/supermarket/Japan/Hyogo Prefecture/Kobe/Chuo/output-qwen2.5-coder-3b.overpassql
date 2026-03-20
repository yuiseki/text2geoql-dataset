[out:json][timeout:30];
area["name:en"="Kobe"][boundary=administrative]->.outer;
area["name:en"="Hyogo Prefecture"]->.inner;
(
  nwr["shop"~"supermarket"](area.inner)(area.outer);
);
out geom;
