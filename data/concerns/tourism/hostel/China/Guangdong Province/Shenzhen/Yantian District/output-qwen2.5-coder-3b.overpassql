[out:json][timeout:30];
area["name:en"="Shenzhen"][boundary=administrative]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
