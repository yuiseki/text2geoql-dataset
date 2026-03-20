[out:json][timeout:30];
area["name:en"="Shenzhen"][boundary=administrative]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["tourism"="guest_house"](area.inner)(area.outer);
);
out geom;
