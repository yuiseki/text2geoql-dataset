[out:json][timeout:30];
area["name:en"="Shenzhen"][boundary=administrative]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
