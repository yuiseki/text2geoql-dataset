[out:json][timeout:30];
area["name:en"="Fukuoka"][boundary=administrative]->.outer;
area["name:en"="Fukuoka Prefecture"]->.inner;
(
  nwr["shop"~"supermarket"](area.inner)(area.outer);
);
out geom;
