[out:json][timeout:30];
area["name:en"="Saitama"][boundary=administrative]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["shop"~"supermarket"](area.inner)(area.outer);
);
out geom;
