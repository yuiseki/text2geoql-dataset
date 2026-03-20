[out:json][timeout:30];
area["name:en"="Shenzhen"][boundary=administrative]->.outer;
area["name:en"="Futian District"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
