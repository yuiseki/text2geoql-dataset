[out:json][timeout:30];
area["name:en"="Saitama"][boundary=administrative]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
